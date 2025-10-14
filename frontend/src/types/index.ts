export interface User {
  id: string;
  name: string;
  email: string;
  points: number;
  level: number;
  searchesRemaining: number;
  contributionsCount: number;
  avatar?: string;
  joinedDate: string;
}

export interface FashionItem {
  id: string;
  imageUrl: string;
  brand: string;
  name: string;
  description: string;
  price: number;
  category: string;
  color: string;
  shoppingLinks: ShoppingLink[];
  confidence: number;
  contributedBy?: string;
  tags: string[];
}

export interface ShoppingLink {
  store: string;
  url: string;
  price: number;
  availability: 'in-stock' | 'out-of-stock' | 'limited';
}

export interface SearchResult {
  id: string;
  originalImage: string;
  items: FashionItem[];
  searchDate: string;
  confidence: number;
}

export interface Contribution {
  id: string;
  userId: string;
  itemId: string;
  type: 'new-item' | 'correction' | 'link-addition';
  points: number;
  date: string;
  status: 'pending' | 'approved' | 'rejected';
}