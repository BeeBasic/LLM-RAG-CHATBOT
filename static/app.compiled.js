
"use strict";

const {
  useState,
  useEffect,
  useRef
} = React;
const App = () => {
  const [theme, setTheme] = useState('light');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });
  };
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.body.className = `${newTheme}-theme`;
  };
  const handleSend = async () => {
    if (!input.trim()) return;
    const newMessages = [...messages, {
      text: input,
      sender: 'user'
    }];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);
    try {
      const response = await fetch('/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: input
        })
      });
      const data = await response.json();
      setMessages([...newMessages, {
        text: data.answer,
        sender: 'bot'
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages([...newMessages, {
        text: 'Sorry, something went wrong.',
        sender: 'bot'
      }]);
    }
    setIsLoading(false);
  };
  return /*#__PURE__*/React.createElement("div", {
    id: "chatbox"
  }, /*#__PURE__*/React.createElement("div", {
    id: "header"
  }, /*#__PURE__*/React.createElement("span", null, "RAG Chatbot"), /*#__PURE__*/React.createElement("button", {
    id: "theme-switcher",
    onClick: toggleTheme
  }, theme === 'light' ? '🌙' : '☀️')), /*#__PURE__*/React.createElement("div", {
    id: "messages"
  }, messages.map((msg, index) => /*#__PURE__*/React.createElement("div", {
    key: index,
    className: `message ${msg.sender}`
  }, /*#__PURE__*/React.createElement("div", {
    className: "bubble"
  }, msg.text))), isLoading && /*#__PURE__*/React.createElement("div", {
    className: "message bot"
  }, /*#__PURE__*/React.createElement("div", {
    className: "bubble"
  }, /*#__PURE__*/React.createElement("div", {
    className: "typing-indicator"
  }, /*#__PURE__*/React.createElement("span", null), /*#__PURE__*/React.createElement("span", null), /*#__PURE__*/React.createElement("span", null)))), /*#__PURE__*/React.createElement("div", {
    ref: messagesEndRef
  })), /*#__PURE__*/React.createElement("div", {
    id: "input-area"
  }, /*#__PURE__*/React.createElement("input", {
    id: "input",
    type: "text",
    placeholder: "Type a message...",
    value: input,
    onChange: e => setInput(e.target.value),
    onKeyPress: e => e.key === 'Enter' && handleSend()
  }), /*#__PURE__*/React.createElement("button", {
    id: "send",
    onClick: handleSend
  }, "Send")));
};
ReactDOM.render( /*#__PURE__*/React.createElement(App, null), document.getElementById('root'));
