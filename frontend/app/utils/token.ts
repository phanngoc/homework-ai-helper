// frontend/app/utils/token.ts

export const getTokenFromLocalStorage = (): string | null => {
    if (typeof window !== 'undefined' && window.localStorage) {
      return localStorage.getItem('authToken');
    }
    return null;
  };