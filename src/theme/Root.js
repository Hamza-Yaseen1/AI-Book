import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import FloatingChatbot from '../components/FloatingChatbot/FloatingChatbot';

function Root({ children }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        {children}
        <FloatingChatbot />
      </motion.div>
    </AnimatePresence>
  );
}

export default Root;
