import { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Box, 
  Container, 
  useTheme, 
  Typography, 
  IconButton, 
  Tooltip,
  Paper,
  Divider,
  Button,
  Chip,
  CircularProgress,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  Fade,
  Zoom,
  Badge,
  Menu,
  MenuItem,
  ClickAwayListener
} from '@mui/material';
import { 
  Send as SendIcon,
  Mic as MicIcon,
  AttachFile as AttachFileIcon,
  SmartToy as BotIcon,
  Person as UserIcon,
  MedicalServices as DiseaseIcon,
  LocalHospital as SymptomIcon,
  Spa as HerbIcon,
  Info as InfoIcon,
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Mood as MoodIcon,
  MoreVert as MoreVertIcon,
  ThumbUp as ThumbUpIcon,
  ThumbUpOutlined as ThumbUpOutlinedIcon,
  InsertEmoticon as InsertEmoticonIcon,
  EmojiEmotions as EmojiEmotionsIcon,
  SentimentSatisfied as SentimentSatisfiedIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  MoodBad as MoodBadIcon,
  SentimentVeryDissatisfied as SentimentVeryDissatisfiedIcon,
  ThumbDown as ThumbDownIcon,
  ThumbDownOutlined as ThumbDownOutlinedIcon
} from '@mui/icons-material';
import { styled, keyframes } from '@mui/material/styles';
import { v4 as uuidv4 } from 'uuid';
import { format, formatDistanceToNow } from 'date-fns';
import { useSnackbar } from 'notistack';
import api from '../services/api';

// Animations
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const pulse = keyframes`
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
`;

// Styled components
const ChatContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 64px)',
  maxHeight: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[2],
  overflow: 'hidden',
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[2],
  overflow: 'hidden',
  border: `1px solid ${theme.palette.divider}`,
}));

const MessageList = styled(Box)({
  flex: 1,
  overflowY: 'auto',
  padding: '16px',
  '& > * + *': {
    marginTop: '12px',
  },
});

const MessageBubble = styled(Box, {
  shouldForwardProp: (prop) => !['isBot', 'isTyping', 'isFirst', 'isLast', 'status'].includes(prop),
})(({ theme, isBot, isTyping, isFirst, isLast, status }) => ({
  maxWidth: '80%',
  padding: '10px 16px',
  borderRadius: theme.shape.borderRadius,
  borderTopLeftRadius: isBot && isFirst ? 4 : theme.shape.borderRadius,
  borderTopRightRadius: !isBot && isFirst ? 4 : theme.shape.borderRadius,
  borderBottomLeftRadius: isBot && isLast ? 4 : theme.shape.borderRadius,
  borderBottomRightRadius: !isBot && isLast ? 4 : theme.shape.borderRadius,
  wordBreak: 'break-word',
  position: 'relative',
  ...(isBot ? {
    backgroundColor: theme.palette.grey[100],
    borderTopLeftRadius: 4,
    marginRight: 'auto',
  } : {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    borderTopRightRadius: 4,
    marginLeft: 'auto',
  }),
  ...(isTyping && {
    '&::after': {
      content: '""',
      display: 'inline-block',
      width: '4px',
      height: '4px',
      borderRadius: '50%',
      backgroundColor: theme.palette.text.primary,
      marginLeft: '4px',
      animation: 'typing 1.4s infinite both',
      '&:nth-child(2)': {
        animationDelay: '0.2s',
      },
      '&:nth-child(3)': {
        animationDelay: '0.4s',
      },
    },
    '@keyframes typing': {
      '0%': { opacity: 0.4, transform: 'translateY(0)' },
      '50%': { opacity: 1, transform: 'translateY(-4px)' },
      '100%': { opacity: 0.4, transform: 'translateY(0)' },
    },
  }),
}));

const SuggestionChip = styled(Chip)(({ theme }) => ({
  margin: '4px',
  cursor: 'pointer',
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

const TypingIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: 4,
  padding: '8px 16px',
  backgroundColor: theme.palette.grey[100],
  borderRadius: 16,
  width: 'fit-content',
  margin: '8px 0',
  animation: `${fadeIn} 0.3s ease-out`,
}));

const TypingDot = styled('div')(({ theme, delay }) => ({
  width: 8,
  height: 8,
  borderRadius: '50%',
  backgroundColor: theme.palette.primary.main,
  animation: `${pulse} 1.5s ease-in-out infinite`,
  animationDelay: `${delay}s`,
}));

const ReactionMenu = styled(Box)(({ theme }) => ({
  position: 'absolute',
  bottom: '100%',
  left: 0,
  display: 'flex',
  gap: 4,
  backgroundColor: theme.palette.background.paper,
  borderRadius: 20,
  padding: '4px 8px',
  boxShadow: theme.shadows[3],
  zIndex: 1,
  '& .MuiIconButton-root': {
    padding: 4,
    '&:hover': {
      transform: 'scale(1.2)',
    },
  },
}));

const MessageStatus = styled(Box)(({ theme, status }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: 4,
  marginLeft: 8,
  fontSize: '0.75rem',
  color: status === 'sent' ? theme.palette.text.secondary : 
        status === 'delivered' ? theme.palette.info.main : 
        status === 'read' ? theme.palette.primary.main : theme.palette.text.disabled,
}));

const MessageTime = styled(Typography)(({ theme }) => ({
  fontSize: '0.6875rem',
  color: 'inherit',
  opacity: 0.7,
  marginLeft: 8,
}));

const MessageActions = styled(Box)(({ theme }) => ({
  position: 'absolute',
  right: 8,
  top: -12,
  backgroundColor: theme.palette.background.paper,
  borderRadius: 16,
  boxShadow: theme.shadows[2],
  display: 'none',
  '&.visible': {
    display: 'flex',
  },
  '& .MuiIconButton-root': {
    padding: 4,
  },
}));

// Reaction emojis
const REACTIONS = [
  { emoji: '👍', label: 'Like' },
  { emoji: '❤️', label: 'Love' },
  { emoji: '😊', label: 'Happy' },
  { emoji: '😮', label: 'Surprised' },
  { emoji: '😢', label: 'Sad' },
  { emoji: '😡', label: 'Angry' },
];

// Message component
const Message = React.memo(({ 
  message, 
  isBot = false, 
  isFirst = true, 
  isLast = true,
  onReact,
  onReply,
  onCopy,
  onDelete
}) => {
  const [showReactions, setShowReactions] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const messageRef = useRef(null);
  const theme = useTheme();
  const { enqueueSnackbar } = useSnackbar();

  const handleContextMenu = (e) => {
    e.preventDefault();
    setAnchorEl(e.currentTarget);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
  };

  const handleReaction = (reaction) => {
    onReact?.(message.id, reaction);
    setShowReactions(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    enqueueSnackbar('Message copied to clipboard', { variant: 'success' });
    handleCloseMenu();
  };

  const handleReply = () => {
    onReply?.(message);
    handleCloseMenu();
  };

  const handleDelete = () => {
    onDelete?.(message.id);
    handleCloseMenu();
  };

  // Format message time
  const formattedTime = message.timestamp ? 
    formatDistanceToNow(new Date(message.timestamp), { addSuffix: true }) : '';

  return (
    <Box
      ref={messageRef}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: isBot ? 'flex-start' : 'flex-end',
        mb: isLast ? 2 : 0.5,
        position: 'relative',
        '&:hover .message-actions': {
          opacity: 1,
          visibility: 'visible',
        },
      }}
    >
      {/* Message bubble */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          maxWidth: '80%',
          position: 'relative',
        }}
      >
        <MessageBubble
          isBot={isBot}
          isFirst={isFirst}
          isLast={isLast}
          status={message.status}
          onContextMenu={handleContextMenu}
          sx={{
            position: 'relative',
            '&:hover .message-actions': {
              opacity: 1,
              visibility: 'visible',
            },
          }}
        >
          {message.content}
          
          {/* Message metadata */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'flex-end',
              alignItems: 'center',
              mt: 0.5,
              gap: 0.5,
            }}
          >
            {message.reactions?.length > 0 && (
              <Box
                sx={{
                  display: 'flex',
                  gap: 0.5,
                  mr: 1,
                  bgcolor: 'rgba(0, 0, 0, 0.1)',
                  borderRadius: 4,
                  px: 1,
                  py: 0.25,
                }}
              >
                {message.reactions.map((reaction, idx) => (
                  <Tooltip key={idx} title={reaction.users.join(', ')}>
                    <Typography variant="caption" sx={{ cursor: 'default' }}>
                      {reaction.emoji}
                    </Typography>
                  </Tooltip>
                ))}
              </Box>
            )}
            
            <MessageTime variant="caption">
              {formattedTime}
            </MessageTime>
            
            {!isBot && message.status && (
              <MessageStatus status={message.status}>
                {message.status === 'sent' && <CheckCircleIcon fontSize="inherit" />}
                {message.status === 'delivered' && <CheckCircleIcon fontSize="inherit" />}
                {message.status === 'read' && <CheckCircleIcon fontSize="inherit" color="primary" />}
                {message.status === 'error' && <CancelIcon fontSize="inherit" color="error" />}
              </MessageStatus>
            )}
          </Box>
          
          {/* Message actions */}
          <MessageActions className={`message-actions`}>
            <Tooltip title="React">
              <IconButton 
                size="small"
                onClick={() => setShowReactions(!showReactions)}
                sx={{ '&:hover': { transform: 'scale(1.2)' } }}
              >
                <MoodIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Reply">
              <IconButton 
                size="small" 
                onClick={handleReply}
                sx={{ '&:hover': { transform: 'scale(1.2)' } }}
              >
                <ReplyIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="More">
              <IconButton 
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  setAnchorEl(e.currentTarget);
                }}
                sx={{ '&:hover': { transform: 'scale(1.2)' } }}
              >
                <MoreVertIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </MessageActions>
        </MessageBubble>
        
        {/* Reaction menu */}
        {showReactions && (
          <ClickAwayListener onClickAway={() => setShowReactions(false)}>
            <ReactionMenu>
              {REACTIONS.map((reaction) => (
                <Tooltip key={reaction.emoji} title={reaction.label}>
                  <IconButton
                    size="small"
                    onClick={() => handleReaction(reaction.emoji)}
                    sx={{ '&:hover': { transform: 'scale(1.5)' } }}
                  >
                    <Typography variant="body1">{reaction.emoji}</Typography>
                  </IconButton>
                </Tooltip>
              ))}
            </ReactionMenu>
          </ClickAwayListener>
        )}
      </Box>
      
      {/* Context menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleCloseMenu}
        onClick={handleCloseMenu}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={handleCopy}>
          <ListItemIcon>
            <FileCopyIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Copy</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleReply}>
          <ListItemIcon>
            <ReplyIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Reply</ListItemText>
        </MenuItem>
        {!isBot && (
          <MenuItem onClick={handleDelete}>
            <ListItemIcon>
              <DeleteIcon fontSize="small" color="error" />
            </ListItemIcon>
            <ListItemText primaryTypographyProps={{ color: 'error' }}>
              Delete
            </ListItemText>
          </MenuItem>
        )}
      </Menu>
    </Box>
  );
});

Message.displayName = 'Message';

// Main ChatPage component
const ChatPage = ({ userData }) => {
  const theme = useTheme();
  const { enqueueSnackbar } = useSnackbar();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [replyingTo, setReplyingTo] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const messegesEndRef = useRef(null);
  const inputRef = useRef(null);
  const emojiPickerRef = useRef(null);
  
  // Sample initial messages
  useEffect(() => {
    setMessages([
      {
        id: '1',
        content: 'Hello! I am your Ayurveda assistant. How can I help you today?',
        sender: 'bot',
        timestamp: new Date(Date.now() - 1000 * 60 * 2), // 2 minutes ago
        status: 'delivered',
        reactions: [
          { emoji: '👍', users: ['User1'] },
          { emoji: '❤️', users: ['User2'] },
        ],
      },
    ]);
  }, []);
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  // Handle sending a new message
  const handleSendMessege = (e) => {
    e?.preventDefault();
    if (!newMessage.trim()) return;
    
    const message = {
      id: Date.now().toString(),
      content: newMessage,
      sender: 'user',
      timestamp: new Date(),
      status: 'sent',
      replyingTo,
      reactions: [],
    };
    
    setMessages(prev => [...prev, message]);
    setNewMessage('');
    setReplyingTo(null);
    setShowEmojiPicker(false);
    
    // Simulate typing indicator after a short delay
    setTimeout(() => {
      setIsTyping(true);
      
      // Simulate bot response after a delay
      setTimeout(() => {
        setIsTyping(false);
        
        const botMessage = {
          id: Date.now().toString(),
          content: 'I am your Ayurveda assistant. How can I help you today?',
          sender: 'bot',
          timestamp: new Date(),
          status: 'delivered',
          reactions: [],
        };
        
        setMessages(prev => [...prev, botMessage]);
      }, 1500);
    }, 1000);
  };
  
  // Handle adding emoji to message
  const handleAddEmoji = (emoji) => {
    setNewMessage(prev => prev + emoji.native);
    setShowEmojiPicker(false);
    inputRef.current.focus();
  };
  
  // Handle reaction to a message
  const handleReactToMessage = (messageId, emoji) => {
    setMessages(prev => 
      prev.map(msg => {
        if (msg.id === messageId) {
          // Check if user already reacted with this emoji
          const reactionIndex = msg.reactions.findIndex(r => r.emoji === emoji);
          let updatedReactions = [...msg.reactions];
          
          if (reactionIndex > -1) {
            // Remove reaction if it exists
            updatedReactions = updatedReactions.filter((_, i) => i !== reactionIndex);
          } else {
            // Add new reaction
            updatedReactions.push({ 
              emoji, 
              users: [userData?.username || 'You'] 
            });
          }
          
          return { ...msg, reactions: updatedReactions };
        }
        return msg;
      })
    );
  };
  
  // Handle reply to a message
  const handleReplyToMessage = (message) => {
    setReplyingTo(message);
    inputRef.current.focus();
  };
  
  // Handle copying message text
  const handleCopyMessage = (text) => {
    navigator.clipboard.writeText(text);
    enqueueSnackbar('Message copied to clipboard', { variant: 'success' });
  };
  
  // Handle deleting a message
  const handleDeleteMessage = (messageId) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
    enqueueSnackbar('Message deleted', { variant: 'info' });
  };
  
  // Handle click outside emoji picker
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (emojiPickerRef.current && !emojiPickerRef.current.contains(event.target)) {
        setShowEmojiPicker(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  const [diseasePrediction, setDiseasePrediction] = useState(null);
  const [showDiseaseDialog, setShowDiseaseDialog] = useState(false);
  const messagesEndRef = useRef(null);

  // Initial greeting
  useEffect(() => {
    const initialMessages = [
      {
        id: uuidv4(),
        text: 'Namaste! I\'m your Ayurvedic health assistant. How can I help you today?',
        isBot: true,
        timestamp: new Date(),
        type: 'text'
      },
      {
        id: uuidv4(),
        text: 'You can ask me about symptoms, get health advice, or learn about Ayurvedic remedies.',
        isBot: true,
        timestamp: new Date(),
        type: 'suggestions',
        suggestions: [
          'I have a headache',
          'What\'s my dosha?',
          'Suggest herbs for digestion',
          'How to reduce stress?'
        ]
      }
    ];
    setMessages(initialMessages);
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Generate typing indicator
  useEffect(() => {
    if (isTyping) {
      const typingMessage = {
        id: 'typing',
        text: '...',
        isBot: true,
        isTyping: true,
        timestamp: new Date(),
        type: 'typing'
      };
      
      setMessages(prev => [...prev, typingMessage]);
      
      return () => {
        setMessages(prev => prev.filter(msg => msg.id !== 'typing'));
      };
    }
  }, [isTyping]);

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;
    
    const userMessage = {
      id: uuidv4(),
      text,
      isBot: false,
      timestamp: new Date(),
      type: 'text'
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);
    
    try {
      // Call the agent service
      const response = await api.post('/api/chat', {
        message: text,
        userId: userData?.id,
        context: {
          previousMessages: messages.slice(-5).map(m => ({
            role: m.isBot ? 'assistant' : 'user',
            content: m.text
  })),
          userData: userData || {}
        }
      });
      
      const botResponse = {
        id: uuidv4(),
        text: response.data.message,
        isBot: true,
        timestamp: new Date(),
        type: 'text',
        metadata: response.data.metadata
      };
      
      // Check if the response includes a disease prediction
      if (response.data.metadata?.isDiseasePrediction) {
        setDiseasePrediction({
          condition: response.data.metadata.condition,
          confidence: response.data.metadata.confidence,
          symptoms: response.data.metadata.symptoms || [],
          recommendations: response.data.metadata.recommendations || []
        });
        setShowDiseaseDialog(true);
      }
      
      // Add any follow-up suggestions
      if (response.data.suggestions?.length > 0) {
        const suggestionsMessage = {
          id: uuidv4(),
          text: 'You might want to know:',
          isBot: true,
          timestamp: new Date(),
          type: 'suggestions',
          suggestions: response.data.suggestions
        };
        setMessages(prev => [...prev, botResponse, suggestionsMessage]);
      } else {
        setMessages(prev => [...prev, botResponse]);
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: uuidv4(),
        text: 'Sorry, I encountered an error. Please try again later.',
        isBot: true,
        timestamp: new Date(),
        type: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };
  
  const handleSuggestionClick = (suggestion) => {
    handleSendMessege(suggestion);
  };
  
  const handleStartDoshaAnalysis = () => {
    // Navigate to Dosha Analysis tab or start a guided analysis in chat
    handleSendMessege("I'd like to take a dosha analysis test.");
  };
  
  const handleCloseDiseaseDialog = () => {
    setShowDiseaseDialog(false);
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 64px)',
        width: '100%',
        overflow: 'hidden',
        bgcolor: 'background.default',
      }}
    >
      <Container 
        maxWidth="xl" 
        sx={{ 
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          py: 2,
        }}
      >
        <ChatContainer>
          <MessageList>
            {messages.map((message) => (
              <Box key={message.id}>
                <Box
                  display="flex"
                  flexDirection={message.isBot ? 'row' : 'row-reverse'}
                  alignItems="flex-start"
                  mb={2}
                >
                  <Avatar
                    sx={{
                      width: 32,
                      height: 32,
                      bgcolor: message.isBot ? 'primary.light' : 'secondary.main',
                      mr: message.isBot ? 1 : 0,
                      ml: message.isBot ? 0 : 1,
                      mt: 0.5,
                    }}
                  >
                    {message.isBot ? <BotIcon /> : <UserIcon />}
                  </Avatar>
                  <Box>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      display="block"
                      textAlign={message.isBot ? 'left' : 'right'}
                      mb={0.5}
                    >
                      {message.isBot ? 'AyurBot' : 'You'}
                    </Typography>
                    <MessageBubble isBot={message.isBot} isTyping={message.isTyping}>
                      {message.type === 'suggestions' ? (
                        <Box>
                          <Typography variant="body1" paragraph>
                            {message.text}
                          </Typography>
                          <Box display="flex" flexWrap="wrap" mt={1}>
                            {message.suggestions.map((suggestion, idx) => (
                              <SuggestionChip
                                key={idx}
                                label={suggestion}
                                size="small"
                                onClick={() => handleSuggestionClick(suggestion)}
                              />
                            ))}
                          </Box>
                        </Box>
                      ) : (
                        <Typography variant="body1">
                          {message.text}
                          {message.isTyping && <><span>.</span><span>.</span><span>.</span></>}
                        </Typography>
                      )}
                      <Typography
                        variant="caption"
                        display="block"
                        textAlign="right"
                        mt={1}
                        color={message.isBot ? 'text.secondary' : 'primary.contrastText'}
                      >
                        {format(new Date(message.timestamp), 'h:mm a')}
                      </Typography>
                    </MessageBubble>
                  </Box>
                </Box>
                
                {message.metadata?.relatedHerbs && (
                  <Box ml={6} mt={-1} mb={2}>
                    <Typography variant="caption" color="text.secondary">
                      Related herbs:
                    </Typography>
                    <Box display="flex" flexWrap="wrap" mt={0.5}>
                      {message.metadata.relatedHerbs.map((herb, idx) => (
                        <Chip
                          key={idx}
                          label={herb.name}
                          size="small"
                          icon={<HerbIcon fontSize="small" />}
                          sx={{ mr: 0.5, mb: 0.5 }}
                          onClick={() => handleSendMessage(`Tell me more about ${herb.name}`)}
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </Box>
            ))}
            <div ref={messagesEndRef} />
          </MessageList>
          
          <Box
            component="form"
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage(inputValue);
            }}
            sx={{
              display: 'flex',
              p: 2,
              borderTop: `1px solid ${theme.palette.divider}`,
              bgcolor: 'background.paper',
            }}
          >
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Type your message..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage(inputValue);
                }
              }}
              InputProps={{
                sx: { borderRadius: 4 },
                startAdornment: (
                  <InputAdornment position="start">
                    <IconButton size="small" onClick={() => {}}>
                      <AttachFileIcon fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton 
                      size="small" 
                      onClick={() => {}}
                      sx={{ mr: 1 }}
                    >
                      <MicIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      type="submit"
                      color="primary"
                      disabled={!inputValue.trim()}
                      sx={{ 
                        bgcolor: 'primary.main',
                        color: 'primary.contrastText',
                        '&:hover': {
                          bgcolor: 'primary.dark',
                        },
                        '&.Mui-disabled': {
                          bgcolor: 'action.disabledBackground',
                          color: 'action.disabled',
                        },
                      }}
                    >
                      <SendIcon fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Box>
        </ChatContainer>
        
        {/* Quick Actions */}
        <Box mt={2} display="flex" justifyContent="center" flexWrap="wrap">
          <Button
            variant="outlined"
            startIcon={<DiseaseIcon />}
            onClick={() => handleSendMessage("I'm not feeling well. Can you help me understand what's wrong?")}
            sx={{ m: 0.5 }}
          >
            Check Symptoms
          </Button>
          <Button
            variant="outlined"
            startIcon={<SymptomIcon />}
            onClick={handleStartDoshaAnalysis}
            sx={{ m: 0.5 }}
          >
            Dosha Analysis
          </Button>
          <Button
            variant="outlined"
            startIcon={<HerbIcon />}
            onClick={() => handleSendMessage("Recommend some Ayurvedic herbs for common ailments")}
            sx={{ m: 0.5 }}
          >
            Herbal Remedies
          </Button>
        </Box>
      </Container>
      
      {/* Disease Prediction Dialog */}
      <Dialog
        open={showDiseaseDialog}
        onClose={handleCloseDiseaseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center">
              <DiseaseIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Health Assessment</Typography>
            </Box>
            <IconButton onClick={handleCloseDiseaseDialog} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {diseasePrediction && (
            <Box>
              <Box mb={3}>
                <Typography variant="subtitle1" gutterBottom>
                  Based on your symptoms, you might have:
                </Typography>
                <Box display="flex" alignItems="center" mb={2}>
                  <Typography variant="h5" color="primary" sx={{ fontWeight: 'bold', mr: 2 }}>
                    {diseasePrediction.condition}
                  </Typography>
                  <Chip 
                    label={`${Math.round(diseasePrediction.confidence * 100)}% confidence`}
                    color={diseasePrediction.confidence > 0.7 ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>
                
                <Typography variant="body2" color="text.secondary" paragraph>
                  <InfoIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                  This is not a medical diagnosis. Please consult a healthcare professional for an accurate assessment.
                </Typography>
              </Box>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                    <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                      <SymptomIcon color="secondary" sx={{ mr: 1 }} />
                      Symptoms Matched
                    </Typography>
                    <List dense>
                      {diseasePrediction.symptoms.map((symptom, idx) => (
                        <ListItem key={idx}>
                          <ListItemAvatar>
                            <Avatar sx={{ bgcolor: 'success.light', width: 24, height: 24 }}>
                              <CheckCircleIcon fontSize="small" sx={{ color: 'white' }} />
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText primary={symptom} />
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                    <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                      <HerbIcon color="primary" sx={{ mr: 1 }} />
                      Recommended Actions
                    </Typography>
                    <List dense>
                      {diseasePrediction.recommendations.map((rec, idx) => (
                        <ListItem key={idx}>
                          <ListItemAvatar>
                            <Avatar sx={{ bgcolor: 'primary.light', width: 24, height: 24 }}>
                              <InfoIcon fontSize="small" sx={{ color: 'white' }} />
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText primary={rec} />
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                </Grid>
              </Grid>
              
              <Box mt={3} textAlign="center">
                <Button 
                  variant="contained" 
                  color="primary" 
                  onClick={handleCloseDiseaseDialog}
                  startIcon={<LocalHospitalIcon />}
                  sx={{ mr: 2 }}
                >
                  Find Nearby Doctors
                </Button>
                <Button 
                  variant="outlined" 
                  onClick={() => {
                    handleCloseDiseaseDialog();
                    handleSendMessage(`Tell me more about ${diseasePrediction.condition}`);
                  }}
                >
                  Learn More
                </Button>
              </Box>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default ChatPage;
