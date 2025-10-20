/**
 * Test constants for credentials and test data.
 *
 * This file centralizes all test credentials to avoid hardcoding them throughout test files.
 * These are ONLY for testing purposes and should NEVER be used in production.
 */

/**
 * Generate a random test password
 */
export const generateTestPassword = (length: number = 12): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
  let password = '';
  const array = new Uint32Array(length);
  crypto.getRandomValues(array);
  for (let i = 0; i < length; i++) {
    password += chars[array[i] % chars.length];
  }
  return password;
};

/**
 * Test user credentials
 */
export const TestCredentials = {
  // Basic test user
  TEST_EMAIL: 'test@example.com',
  TEST_USERNAME: 'testuser',
  TEST_PASSWORD: process.env.TEST_PASSWORD || 'TestPass123!',

  // Admin test user
  ADMIN_EMAIL: 'admin@test.com',
  ADMIN_USERNAME: 'adminuser',
  ADMIN_PASSWORD: process.env.TEST_ADMIN_PASSWORD || 'AdminPass123!',

  // Alternative test users
  TEST_EMAIL_2: 'test2@example.com',
  TEST_USERNAME_2: 'testuser2',

  // Specific test scenarios
  USER_EMAIL: 'user@example.com',
  NEW_EMAIL: 'new@example.com',
  JOHN_EMAIL: 'john@example.com',

  // Invalid credentials for testing
  WRONG_PASSWORD: 'WrongPass123!',
  INVALID_EMAIL: 'not-an-email',
} as const;

/**
 * Mock user data for testing
 */
export const createMockUser = (overrides?: Partial<{
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at: string;
}>) => ({
  id: 1,
  email: TestCredentials.TEST_EMAIL,
  username: TestCredentials.TEST_USERNAME,
  full_name: 'Test User',
  role: 'user' as const,
  is_active: true,
  created_at: new Date().toISOString(),
  ...overrides,
});

/**
 * Mock admin user data for testing
 */
export const createMockAdminUser = (overrides?: Partial<{
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at: string;
}>) => ({
  id: 1,
  email: TestCredentials.ADMIN_EMAIL,
  username: TestCredentials.ADMIN_USERNAME,
  full_name: 'Admin User',
  role: 'admin' as const,
  is_active: true,
  created_at: new Date().toISOString(),
  ...overrides,
});

/**
 * Mock authentication response
 */
export const createMockAuthResponse = (token: string = 'mock-jwt-token') => ({
  access_token: token,
  token_type: 'bearer',
});

/**
 * API test constants
 */
export const APITestConstants = {
  TEST_ORIGIN: 'http://localhost:5173',
  TEST_API_URL: 'http://localhost:8000',
  MOCK_TOKEN: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock.token',
} as const;
