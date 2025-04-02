document.addEventListener('DOMContentLoaded', function() {
  // Check if the React ChatComponent is mounted by looking for an element with the id 'react-chat'
  // The React ChatComponent should render its container with this id
  if (!document.getElementById('react-chat')) {
    console.log('Legacy chat fallback is active because React ChatComponent is not mounted.');
    
    // Initialize legacy chat functionality here as a fallback
    // The legacy chat code below is maintained in case the React component fails to mount.

    // Example legacy chat initialization
    var legacyChatContainer = document.getElementById('legacy-chat');
    if (legacyChatContainer) {
      legacyChatContainer.innerHTML = '<p>Legacy Chat Initialized. This is a fallback chat interface.</p>';

      // Additional legacy chat functions can be added here if needed
      // For now, this is a placeholder to indicate fallback activation.
    } else {
      console.warn('Legacy chat container not found. No legacy chat interface to initialize.');
    }
  } else {
    console.log('React ChatComponent detected. Legacy chat functionality is disabled to prevent conflicts.');
  }
});
