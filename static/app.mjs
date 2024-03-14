import { h, render } from 'https://esm.sh/preact';
import {
  useCallback,
  useReducer,
  useState,
  useRef,
  useEffect,
} from 'https://esm.sh/preact/hooks';
import htm from 'https://esm.sh/htm';

const GITHUB_LINK = 'https://github.com/Scthe/rag-chat-with-context';

/** 'ws://localhost:8080/ws' */
const SOCKET_URL = `ws://${location.host}/ws`;

const SOCKET_STATE = {
  connecting: 'connecting',
  open: 'open',
  closed: 'closed',
};

const MSG_TYPE = {
  user: 'user',
  ai: 'ai',
  system: 'system',
};

const SYSTEM_MSG_TYPE = {
  contextReset: 'contextReset',
  socketConnected: 'socketConnected',
  socketDisconnected: 'socketDisconnected',
  intro: 'intro',
};
const SYSTEM_MSG_PROPS = {
  contextReset: { text: 'Chat context reset' },
  socketConnected: { text: 'Socket connected' },
  socketDisconnected: { text: 'Error: Socket disconnected', isError: true },
  intro: { isIntro: true },
};

// Initialize htm with Preact
const html = htm.bind(h);

const HARD_SPACE = '\u00A0';

const toggleElementInArr = (arr, item) =>
  arr.includes(item) ? arr.filter((i) => i !== item) : [...arr, item];

function MessageMeta({ type, meta }) {
  const [expanded, setExpanded] = useState([]);

  const toggleSource = (idx) => {
    setExpanded((exps) => toggleElementInArr(exps, idx));
  };
  const isSrcExpanded = (idx) => expanded.includes(idx);

  meta = type === MSG_TYPE.ai ? meta : undefined;
  if (meta == undefined) {
    return undefined;
  }

  const { elapsed, sources, inferred_question } = meta;
  const wikiLink = (s) => html`<a
    href=${s.url}
    rel="noopener noreferrer"
    target="_blank"
    >${s.filename}</a
  >`;
  const score = (s) =>
    html`Score=<span class="colored">${s.score.toFixed(5)}</span>`;
  const tokenCount = (s) => html`<span class="colored"
    >Token count: ${s.token_count}</span
  >`;

  return html`<div class="message-meta">
    <p>Elapsed: <span class="colored">${elapsed.toFixed(2)}s</span></p>
    <p>Inferred question: <span class="colored">${inferred_question}</span></p>
    <div>
      <ul>
        ${sources.map(
          (s, idx) => html`<li key="${idx}">
            Based on:${HARD_SPACE}${wikiLink(s)},${HARD_SPACE}${score(s)}
            <button
              type="button"
              class="toggle-source-btn reset-focus-states"
              onclick=${() => toggleSource(idx)}
            >
              ${isSrcExpanded(idx) ? '-' : '+'}
            </button>
            ${isSrcExpanded(idx)
              ? html`<p class="source-text">
                  ${s.content}<br />${tokenCount(s)}
                </p>`
              : undefined}
          </li>`
        )}
      </ul>
    </div>
  </div>`;
}

function Message({ type, text, meta, error, status }) {
  // console.log({ ...arguments[0] });
  meta = type === MSG_TYPE.ai ? meta : undefined;

  const systemMsgProps = SYSTEM_MSG_PROPS[status];
  // console.log(systemMsgProps);
  text =
    type === MSG_TYPE.system && systemMsgProps && systemMsgProps.text
      ? systemMsgProps.text
      : text;
  text = type === MSG_TYPE.ai && error ? `Error: ${error}` : text;

  const cl = cx('message', {
    'message-user': type === MSG_TYPE.user,
    'message-system': type === MSG_TYPE.system,
    'message-system-error': type === MSG_TYPE.system && systemMsgProps?.isError,
    'message-system-intro': type === MSG_TYPE.system && systemMsgProps?.isIntro,
    'message-ai': type === MSG_TYPE.ai,
    'message-ai-empty': type === MSG_TYPE.ai && text.length == 0,
    'message-ai-error': type === MSG_TYPE.ai && error,
  });
  return html`<li class="${cl}">
    <p class="message-text">${text || HARD_SPACE}</p>
    <${MessageMeta} type=${type} meta=${meta} />
  </li>`;
}

function MessageContainer({ messages }) {
  return html`<div class="message-container-wrapper">
    <ul>
      ${messages.map((m) => html`<${Message} key="${m.id}" ...${m} />`)}
    </ul>
  </div>`;
}

function UserInput({
  actionSendMessage,
  actionResetContext,
  actionReconnect,
  socketState,
}) {
  const iconSize = '30px';
  const sendIcon = html`<svg
    xmlns="http://www.w3.org/2000/svg"
    width="${iconSize}"
    height="${iconSize}"
    fill="currentcolor"
    viewBox="0 0 256 256"
    aria-hidden="true"
  >
    <path
      d="M231.4,44.34s0,.1,0,.15l-58.2,191.94a15.88,15.88,0,0,1-14,11.51q-.69.06-1.38.06a15.86,15.86,0,0,1-14.42-9.15l-35.71-75.39a4,4,0,0,1,.79-4.54l57.26-57.27a8,8,0,0,0-11.31-11.31L97.08,147.6a4,4,0,0,1-4.54.79l-75-35.53A16.37,16.37,0,0,1,8,97.36,15.89,15.89,0,0,1,19.57,82.84l191.94-58.2.15,0A16,16,0,0,1,231.4,44.34Z"
    ></path>
  </svg>`;

  const resetCtxIcon = html`<svg
    xmlns="http://www.w3.org/2000/svg"
    width="${iconSize}"
    height="${iconSize}"
    fill="currentcolor"
    viewBox="0 0 256 256"
    aria-hidden="true"
  >
    <path
      d="M235.5,216.81c-22.56-11-35.5-34.58-35.5-64.8V134.73a15.94,15.94,0,0,0-10.09-14.87L165,110a8,8,0,0,1-4.48-10.34l21.32-53a28,28,0,0,0-16.1-37,28.14,28.14,0,0,0-35.82,16,.61.61,0,0,0,0,.12L108.9,79a8,8,0,0,1-10.37,4.49L73.11,73.14A15.89,15.89,0,0,0,55.74,76.8C34.68,98.45,24,123.75,24,152a111.45,111.45,0,0,0,31.18,77.53A8,8,0,0,0,61,232H232a8,8,0,0,0,3.5-15.19ZM115.11,216a87.53,87.53,0,0,1-24.34-42,8,8,0,0,0-15.49,4,105.16,105.16,0,0,0,18.36,38H64.44A95.54,95.54,0,0,1,40,152a85.9,85.9,0,0,1,7.73-36.29l137.8,55.12c3,18,10.56,33.48,21.89,45.16Z"
    ></path>
  </svg>`;

  const reconnectIcon = html`<svg
    xmlns="http://www.w3.org/2000/svg"
    width="${iconSize}"
    height="${iconSize}"
    fill="currentcolor"
    viewBox="0 0 256 256"
    aria-hidden="true"
  >
    <path
      d="M197.66,186.34a8,8,0,0,1,0,11.32C196.58,198.73,170.82,224,128,224c-23.36,0-46.13-9.1-66.28-26.41L45.66,213.66A8,8,0,0,1,32,208V160a8,8,0,0,1,8-8H88a8,8,0,0,1,5.66,13.66L73.08,186.24C86.08,197.15,104.83,208,128,208c36.27,0,58.13-21.44,58.34-21.66A8,8,0,0,1,197.66,186.34Zm21.4-145.73a8,8,0,0,0-8.72,1.73L194.28,58.41C174.13,41.1,151.36,32,128,32,85.18,32,59.42,57.27,58.34,58.34A8,8,0,0,0,69.66,69.66C69.87,69.44,91.73,48,128,48c23.17,0,41.92,10.85,54.92,21.76L162.34,90.34A8,8,0,0,0,168,104h48a8,8,0,0,0,8-8V48A8,8,0,0,0,219.06,40.61Z"
    ></path>
  </svg>`;

  const githubIcon = html`<svg
    xmlns="http://www.w3.org/2000/svg"
    width="${iconSize}"
    height="${iconSize}"
    fill="currentcolor"
    viewBox="0 0 24 24"
    aria-hidden="true"
  >
    <path
      d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
    />
  </svg>`;

  const sendMessagesRef = useRef([]);
  const prevMessagesIndexRef = useRef(-1);

  const onInputKeyDown = useCallback((e) => {
    const inputEl = document.getElementById('user-input-field');
    const msgIdxMods = { ArrowUp: 1, ArrowDown: -1 };
    const msgIdxMod = msgIdxMods[e.code];
    if (msgIdxMod == null || !inputEl) {
      prevMessagesIndexRef.current = -1;
      return;
    }
    e.preventDefault();
    const historyMsgIdx = prevMessagesIndexRef.current + msgIdxMod;
    const historicalMsg = sendMessagesRef.current[historyMsgIdx];
    if (historicalMsg != null) {
      inputEl.value = historicalMsg;
      prevMessagesIndexRef.current = historyMsgIdx;
    }
  }, []);

  const onMessageSend = useCallback(
    (e) => {
      e.preventDefault();
      const inputEl = document.getElementById('user-input-field');
      let text = inputEl.value.trim();
      if (text.length === 0) return;

      sendMessagesRef.current.unshift(text);
      inputEl.value = '';
      actionSendMessage(text);
    },
    [actionSendMessage]
  );

  const onContextReset = useCallback(
    (e) => {
      e.preventDefault();
      actionResetContext();
    },
    [actionResetContext]
  );

  const onReconnect = useCallback(
    (e) => {
      e.preventDefault();
      actionReconnect();
    },
    [actionReconnect]
  );

  if (socketState === SOCKET_STATE.closed) {
    return html`<div class="user-input">
      <button
        type="button"
        title="Try reconnect"
        class="user-input-reconnect-btn reset-focus-states"
        onClick=${onReconnect}
      >
        <p>Try reconnect</p>
        ${reconnectIcon}
      </button>
    </div>`;
  }

  if (socketState === SOCKET_STATE.connecting) {
    return html`<div class="user-input user-input-reconnecting">
      <p>Connecting...</p>
    </div>`;
  }

  return html`<div class="user-input">
    <form onSubmit=${onMessageSend}>
      <div class="user-input-content">
        <div>
          <a
            href=${GITHUB_LINK}
            title="See the repo on GitHub"
            target="_blank"
            rel="noopener noreferrer"
            class="github-btn reset-focus-states"
          >
            ${githubIcon}
          </a>
          <button
            type="button"
            title="Reset the context"
            class="user-input-side-btn reset-focus-states"
            onClick=${onContextReset}
          >
            ${resetCtxIcon}
          </button>
        </div>
        <input
          id="user-input-field"
          name="user-input-field"
          class="user-input-field"
          placeholder="Ask me a question related to Genshin Impact!"
          autocomplete="off"
          onkeydown=${onInputKeyDown}
        />
        <div>
          <button
            type="submit"
            title="Ask the question"
            class="user-input-side-btn reset-focus-states"
          >
            ${sendIcon}
          </button>
        </div>
      </div>
    </form>
  </div>`;
}

function App() {
  const {
    state,
    socketState,
    actionReconnect,
    actionSendMessage,
    actionResetContext,
  } = useMessagesState();
  const { messages } = state;

  const isWindowScrolledBtmRef = useIsWindowScrolledToBottomRef();

  useEffect(() => {
    if (isWindowScrolledBtmRef.current) {
      window.scrollTo({
        top: document.body.offsetHeight,
        behavior: 'smooth',
      });
    }
  }, [messages]);

  return html`<main class="app-container">
    <${MessageContainer} messages=${messages} />
    <${UserInput}
      actionSendMessage=${actionSendMessage}
      actionResetContext=${actionResetContext}
      actionReconnect=${actionReconnect}
      socketState=${socketState}
    />
  </main>`;
}

render(html`<${App} />`, app);

function cx(...args) {
  return args
    .flatMap((part) => {
      switch (typeof part) {
        case 'string':
          return [part];
        case 'undefined':
        case 'boolean':
          return [''];
        case 'object':
          return Object.entries(part).map(([k, v]) => (Boolean(v) ? k : ''));
        default:
          throw new Error('Invalid agument for cx:', JSON.stringify(part));
      }
    })
    .join(' ');
}

function messagesReducer(state, action) {
  console.log('ACTION', action);
  const createMessage = (type, id, rest) => ({
    id: id || randId(),
    type,
    ...rest,
  });

  switch (action.action) {
    case 'send': {
      return {
        ...state,
        messages: [
          ...state.messages,
          createMessage(MSG_TYPE.user, undefined, { text: action.text }),
          createMessage(MSG_TYPE.ai, action.respMsgId, { text: '' }),
        ],
      };
    }
    case 'ai-token': {
      const { token, msgId } = action;
      return {
        ...state,
        messages: updateMessage(msgId, (m) => {
          m.text += token;
        }),
      };
    }
    case 'ai-done': {
      const { msgId, ...rest } = action;
      return {
        ...state,
        messages: updateMessage(msgId, (m) => {
          m.meta = rest;
        }),
      };
    }
    case 'ai-error': {
      const { msgId, error } = action;
      return {
        ...state,
        messages: updateMessage(msgId, (m) => {
          m.error = error;
        }),
      };
    }
    case 'system-msg': {
      const msg = createMessage(MSG_TYPE.system, undefined, {
        status: action.status,
      });
      return {
        ...state,
        messages: [...state.messages, msg],
      };
    }
  }

  function updateMessage(id, fn) {
    return state.messages.map((m) => {
      if (m.id === id) {
        fn(m);
      }
      return m;
    });
  }

  throw Error(`Unknown action '${action.action}'.`);
}

let IS_FIRST_TIME_CONNECTING = true; // A bit hack, but..

function instructionMsg(text) {
  return {
    id: randId(),
    type: MSG_TYPE.system,
    text,
    status: SYSTEM_MSG_TYPE.intro,
  };
}

function useMessagesState() {
  const [state, dispatch] = useReducer(messagesReducer, {
    messages: [
      instructionMsg('Welcome to unofficial Genshin Impact wiki chat!'),
      instructionMsg(
        'It uses Retrieval-augmented generation to formulate the answers.'
      ),
      instructionMsg('Here are a few questions to get you started:'),
      instructionMsg('- Who is Diluc?'),
      instructionMsg("- What is the name of Jean's sister?"),
      instructionMsg('- Compare Mondstadt and Liyue'),
    ],
  });

  const socket = useSocket(SOCKET_URL, (msg) => {
    const { msgId, type } = msg;

    switch (type) {
      case 'token': {
        const { token } = msg;
        dispatch({ action: 'ai-token', msgId, token });
        break;
      }
      case 'done': {
        dispatch({
          action: 'ai-done',
          ...msg,
          msgId,
        });
        break;
      }
      case 'error': {
        const { msgId, error } = msg;
        dispatch({ action: 'ai-error', msgId, error });
        break;
      }
    }
  });

  useEffect(() => {
    switch (socket.status) {
      case SOCKET_STATE.open: {
        dispatch({
          action: 'system-msg',
          status: SYSTEM_MSG_TYPE.socketConnected,
        });

        // loses context on reconnect. Inform user about this
        if (!IS_FIRST_TIME_CONNECTING) {
          dispatch({
            action: 'system-msg',
            status: SYSTEM_MSG_TYPE.contextReset,
          });
        }
        IS_FIRST_TIME_CONNECTING = false;
        break;
      }
      case SOCKET_STATE.closed: {
        dispatch({
          action: 'system-msg',
          status: SYSTEM_MSG_TYPE.socketDisconnected,
        });
        break;
      }
    }
  }, [socket.status]);

  const actionSendMessage = useCallback(
    (text) => {
      const respMsgId = randId();
      dispatch({ action: 'send', text, respMsgId });
      socket.sendMessage({ type: 'query', text, msgId: respMsgId });
    },
    [dispatch, socket.sendMessage]
  );

  const actionResetContext = useCallback(() => {
    dispatch({ action: 'system-msg', status: SYSTEM_MSG_TYPE.contextReset });
    socket.sendMessage({ type: 'reset-context' });
  }, [dispatch, socket.sendMessage]);

  return {
    state,
    socketState: socket.status,
    actionSendMessage,
    actionResetContext,
    actionReconnect: socket.reconnect,
  };
}

function useSocket(url, onMessage) {
  const [status, setStatus] = useState(SOCKET_STATE.connecting);
  const [socket, setSocket] = useState(undefined); // TODO [low] handle url change (NOPE!)
  const onMessageRef = useLatest(onMessage);

  const reloadSocket = useCallback(() => {
    const socket = new WebSocket(url);
    socket.addEventListener('open', () => {
      setSocket(socket);
      setStatus(SOCKET_STATE.open);
    });

    socket.addEventListener('message', (event) => {
      const msg = JSON.parse(event.data);
      console.log('Socket rcv ', msg);
      onMessageRef.current?.(msg);
    });

    socket.addEventListener('close', () => {
      console.log('Socket closed.');
      setStatus(SOCKET_STATE.closed);
      setSocket(undefined);
    });
    return socket;
  }, []);

  useEffect(() => {
    const socket = reloadSocket();

    return () => {
      socket?.close();
      setSocket(undefined);
    };
  }, [reloadSocket]);

  const sendMessage = useCallback((msg) => {
    console.log('Socket sending ', msg);
    socket?.send(JSON.stringify(msg));
  });

  const reconnect = useCallback(() => {
    if (status === SOCKET_STATE.closed && !socket) {
      console.log('Reconnecting..');
      setStatus(SOCKET_STATE.connecting);
      reloadSocket();
    } else {
      console.log('No need for reconnect', { status, socket });
    }
  }, [status, socket]);

  return { status, sendMessage, reconnect };
}

function useLatest(value) {
  const ref = useRef(value);
  ref.current = value;
  return ref;
}

function randId() {
  return Math.random()
    .toString(36)
    .replace(/[^a-z]+/g, '')
    .substr(2, 10);
}

function useIsWindowScrolledToBottomRef() {
  const resultRef = useRef(isWindowScrolledToBottom());

  useEffect(() => {
    function scrollHandler() {
      resultRef.current = isWindowScrolledToBottom();
    }
    window.addEventListener('scroll', scrollHandler);
    return () => {
      window.removeEventListener('scroll', scrollHandler);
    };
  }, []);

  return resultRef;
}

function isWindowScrolledToBottom(margin = 50) {
  const scrollPos = window.innerHeight + window.scrollY;
  const distanceToBottom = document.body.offsetHeight - scrollPos;
  /*console.log(distanceToBottom, {
    innerHeight: window.innerHeight,
    scrollY: window.scrollY,
    document_body_offsetHeight: document.body.offsetHeight,
  });*/
  return distanceToBottom < margin;
}
