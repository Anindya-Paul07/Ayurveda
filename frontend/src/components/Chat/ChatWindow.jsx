import { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  TextField, 
  IconButton, 
  Typography, 
  Switch, 
  CircularProgress,
  Tooltip,
  Zoom
} from '@mui/material';
import { Send, AutoFixHigh, Info as InfoIcon } from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { styled } from '@mui/material/styles';

const MessageBubble = styled(Paper)(({ theme, sender }) => ({
  maxWidth: '80%',
  padding: theme.spacing(1.5, 2),
  marginBottom: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: sender === 'user' 
    ? theme.palette.primary.main 
    : theme.palette.grey[100],
  color: sender === 'user' 
    ? theme.palette.primary.contrastText 
    : theme.palette.text.primary,
  alignSelf: sender === 'user' ? 'flex-end' : 'flex-start',
  boxShadow: theme.shadows[1],
  whiteSpace: 'pre-wrap',
  wordBreak: 'break-word',
  '& a': {
    color: theme.palette.primary.main,
    textDecoration: 'none',
    '&:hover': {
      textDecoration: 'underline',
    },
  },
  '& code': {
    backgroundColor: theme.palette.mode === 'dark' ? 'rgba(0,0,0,0.2)' : 'rgba(0,0,0,0.05)',
    padding: '0.2em 0.4em',
    borderRadius: theme.shape.borderRadius,
    fontFamily: 'monospace',
  },
}));

const ChatWindow = () => {
  const [messages, setMessages] = useState([
    {
      text: 'Namaste! I am your Ayurveda AI assistant. How can I help you today?',
      sender: 'bot',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isAgentic, setIsAgentic] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const theme = useTheme();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    const userInput = input.trim();
    if (!userInput) return;
    
    // Add user message
    const userMessage = { 
      text: userInput, 
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call the appropriate API based on mode
      const endpoint = isAgentic ? '/api/agent/chat' : '/api/chat';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ 
          message: userInput,
          timestamp: new Date().toISOString()
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      setMessages(prev => [...prev, { 
        text: data.response || 'I apologize, but I encountered an issue processing your request.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        metadata: data.metadata
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        text: 'I\'m sorry, I encountered an error. Please try again in a moment.', 
        sender: 'bot',
        timestamp: new Date().toISOString(),
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatMessage = (text) => {
    // Simple markdown-like formatting
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
      .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
      .replace(/\n/g, '<br />') // New lines
      .replace(/`(.*?)`/g, '<code>$1</code>') // Inline code
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'); // Links
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100%',
      maxWidth: '1200px',
      margin: '0 auto',
      p: { xs: 1, sm: 2 },
      gap: 2
    }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        flexDirection: { xs: 'column', sm: 'row' },
        justifyContent: 'space-between', 
        alignItems: { xs: 'stretch', sm: 'center' },
        gap: 1,
        p: 2,
        bgcolor: 'background.paper',
        borderRadius: 2,
        boxShadow: 1,
        position: 'sticky',
        top: 0,
        zIndex: 10
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>Ayurveda AI Assistant</Typography>
          <Tooltip 
            title={
              <Box sx={{ p: 1 }}>
                <Typography variant="caption" component="div">
                  <strong>Standard Mode:</strong> Basic Q&A using the knowledge base
                </Typography>
                <Typography variant="caption" component="div">
                  <strong>Agentic Mode:</strong> Advanced reasoning with multiple tools
                </Typography>
              </Box>
            }
            arrow
            TransitionComponent={Zoom}
          >
            <InfoIcon color="action" fontSize="small" />
          </Tooltip>
        </Box>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center',
          bgcolor: 'action.hover',
          borderRadius: 4,
          p: 0.5,
          width: 'fit-content',
          alignSelf: { xs: 'flex-start', sm: 'center' }
        }}>
          <Typography 
            variant="body2" 
            sx={{ 
              px: 1.5, 
              py: 0.5, 
              borderRadius: 4,
              bgcolor: !isAgentic ? 'background.paper' : 'transparent',
              boxShadow: !isAgentic ? 1 : 'none',
              fontWeight: !isAgentic ? 600 : 400,
              cursor: 'pointer',
              transition: 'all 0.2s',
              '&:hover': {
                bgcolor: 'action.selected',
              }
            }}
            onClick={() => !isAgentic && setIsAgentic(false)}
          >
            Standard
          </Typography>
          <Switch 
            size="small"
            checked={isAgentic} 
            onChange={(e) => setIsAgentic(e.target.checked)} 
            color="primary"
            sx={{
              '& .MuiSwitch-switchBase': {
                '&.Mui-checked': {
                  '& + .MuiSwitch-track': {
                    bgcolor: 'primary.main',
                  },
                },
              },
            }}
          />
          <Typography 
            variant="body2" 
            sx={{ 
              px: 1.5, 
              py: 0.5, 
              borderRadius: 4,
              bgcolor: isAgentic ? 'primary.light' : 'transparent',
              color: isAgentic ? 'primary.contrastText' : 'text.primary',
              boxShadow: isAgentic ? 1 : 'none',
              fontWeight: isAgentic ? 600 : 400,
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              '&:hover': {
                bgcolor: isAgentic ? 'primary.dark' : 'action.selected',
              }
            }}
            onClick={() => !isAgentic && setIsAgentic(true)}
          >
            <AutoFixHigh fontSize="small" />
            <span>Agentic</span>
          </Typography>
        </Box>
      </Box>

      {/* Messages */}
      <Box sx={{ 
        flex: 1, 
        overflowY: 'auto', 
        p: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
        '&::-webkit-scrollbar': {
          width: '8px',
        },
        '&::-webkit-scrollbar-track': {
          bgcolor: 'background.paper',
        },
        '&::-webkit-scrollbar-thumb': {
          bgcolor: 'divider',
          borderRadius: '4px',
          '&:hover': {
            bgcolor: 'text.secondary',
          },
        },
      }}>
        {messages.map((msg, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              '&:hover .message-timestamp': {
                opacity: 1,
              },
            }}
          >
            <MessageBubble 
              elevation={2}
              sender={msg.sender}
              sx={{
                opacity: msg.isError ? 0.9 : 1,
                borderLeft: msg.isError 
                  ? `3px solid ${theme.palette.error.main}` 
                  : 'none',
              }}
            >
              <div 
                dangerouslySetInnerHTML={{ 
                  __html: formatMessage(msg.text) 
                }} 
              />
            </MessageBubble>
            <Typography 
              variant="caption" 
              color="text.secondary"
              className="message-timestamp"
              sx={{
                opacity: 0,
                transition: 'opacity 0.2s',
                px: 1,
                fontSize: '0.7rem',
              }}
            >
              {new Date(msg.timestamp).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </Typography>
          </Box>
        ))}
        {isLoading && (
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'flex-start',
            px: 2,
            py: 1
          }}>
            <Box
              sx={{
                display: 'flex',
                gap: 1,
                bgcolor: 'background.paper',
                p: 1.5,
                borderRadius: 4,
                boxShadow: 1,
              }}
            >
              {[...Array(3)].map((_, i) => (
                <Box
                  key={i}
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    bgcolor: 'primary.main',
                    animation: 'pulse 1.4s infinite',
                    animationDelay: `${i * 0.2}s`,
                    '@keyframes pulse': {
                      '0%': { opacity: 0.3, transform: 'scale(0.8)' },
                      '50%': { opacity: 1, transform: 'scale(1.2)' },
                      '100%': { opacity: 0.3, transform: 'scale(0.8)' },
                    },
                  }}
                />
              ))}
            </Box>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input */}
      <Box sx={{ 
        position: 'sticky',
        bottom: 0,
        bgcolor: 'background.default',
        pt: 1,
        pb: 2,
        borderTop: `1px solid ${theme.palette.divider}`,
      }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center',
          gap: 1,
          bgcolor: 'background.paper',
          borderRadius: 4,
          p: 1,
          boxShadow: 3,
          border: `1px solid ${theme.palette.divider}`,
          '&:focus-within': {
            borderColor: 'primary.main',
            boxShadow: `0 0 0 2px ${theme.palette.primary.main}33`,
          },
          transition: 'all 0.2s',
        }}>
          <TextField
            fullWidth
            variant="standard"
            placeholder="Ask me anything about Ayurveda..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && !isLoading && handleSend()}
            multiline
            maxRows={4}
            disabled={isLoading}
            sx={{ 
              '& .MuiInputBase-root': {
                px: 1.5,
                '&:before, &:after': {
                  display: 'none',
                },
              },
              '& .MuiInputBase-input': {
                '&::placeholder': {
                  opacity: 0.7,
                },
              },
            }}
            InputProps={{
              disableUnderline: true,
            }}
          />
          <IconButton 
            color="primary" 
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            sx={{ 
              alignSelf: 'flex-end',
              mb: 0.5,
              '&.Mui-disabled': {
                color: 'text.disabled',
              },
            }}
          >
            {isLoading ? (
              <CircularProgress size={24} />
            ) : (
              <Send />
            )}
          </IconButton>
        </Box>
        <Typography 
          variant="caption" 
          color="text.secondary"
          sx={{ 
            display: 'block', 
            textAlign: 'center', 
            mt: 1,
            fontSize: '0.7rem',
          }}
        >
          {isAgentic 
            ? 'Agentic mode: Using advanced reasoning and tools'
            : 'Standard mode: Basic knowledge base search'}
        </Typography>
      </Box>
    </Box>
  );
};

export default ChatWindow;
