import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUserPoints: (points: number) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Check for existing session
    const savedUser = localStorage.getItem('snapmyfit-user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const login = async (email: string, password: string) => {
    // Mock login - in real app, this would call your auth API
    const mockUser: User = {
      id: '1',
      name: email.split('@')[0],
      email,
      points: 150,
      level: 2,
      searchesRemaining: 8,
      contributionsCount: 3,
      joinedDate: '2024-01-15',
    };
    setUser(mockUser);
    localStorage.setItem('snapmyfit-user', JSON.stringify(mockUser));
  };

  const register = async (name: string, email: string, password: string) => {
    // Mock registration
    const mockUser: User = {
      id: '1',
      name,
      email,
      points: 50,
      level: 1,
      searchesRemaining: 5,
      contributionsCount: 0,
      joinedDate: new Date().toISOString().split('T')[0],
    };
    setUser(mockUser);
    localStorage.setItem('snapmyfit-user', JSON.stringify(mockUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('snapmyfit-user');
  };

  const updateUserPoints = (points: number) => {
    if (user) {
      const updatedUser = { ...user, points: user.points + points };
      setUser(updatedUser);
      localStorage.setItem('snapmyfit-user', JSON.stringify(updatedUser));
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, updateUserPoints }}>
      {children}
    </AuthContext.Provider>
  );
};