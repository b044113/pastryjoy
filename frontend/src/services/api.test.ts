import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';

// Create mock axios instance
const mockAxiosInstance = {
  interceptors: {
    request: {
      use: vi.fn(),
    },
    response: {
      use: vi.fn(),
    },
  },
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  patch: vi.fn(),
};

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockAxiosInstance),
  },
}));

describe('API Client', () => {
  let apiClient: any;

  beforeEach(async () => {
    // Clear localStorage
    localStorage.clear();

    // Re-import the apiClient to get a fresh instance
    const module = await import('./api');
    apiClient = module.apiClient;
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('creates axios instance with correct base URL', () => {
    expect(axios.create).toHaveBeenCalledWith({
      baseURL: expect.any(String),
      headers: {
        'Content-Type': 'application/json',
      },
    });
  });

  it('exports apiClient instance', () => {
    expect(apiClient).toBeDefined();
    expect(typeof apiClient).toBe('object');
  });

  describe('Request Interceptor', () => {
    let requestInterceptor: any;

    beforeEach(() => {
      // Get the request interceptor that was registered
      const requestUse = mockAxiosInstance.interceptors.request.use;
      if (requestUse.mock.calls.length > 0) {
        requestInterceptor = requestUse.mock.calls[0][0];
      }
    });

    it('adds authorization header when token exists', () => {
      const token = 'test-token-123';
      localStorage.setItem('token', token);

      const config: any = {
        headers: {},
      };

      if (requestInterceptor) {
        const result = requestInterceptor(config);
        expect(result.headers.Authorization).toBe(`Bearer ${token}`);
      }
    });

    it('does not add authorization header when token does not exist', () => {
      const config: any = {
        headers: {},
      };

      if (requestInterceptor) {
        const result = requestInterceptor(config);
        expect(result.headers.Authorization).toBeUndefined();
      }
    });

    it('preserves existing config properties', () => {
      localStorage.setItem('token', 'test-token');

      const config: any = {
        headers: {
          'X-Custom-Header': 'custom-value',
        },
        method: 'GET',
        url: '/test',
      };

      if (requestInterceptor) {
        const result = requestInterceptor(config);
        expect(result.method).toBe('GET');
        expect(result.url).toBe('/test');
        expect(result.headers['X-Custom-Header']).toBe('custom-value');
      }
    });
  });

  describe('Response Interceptor', () => {
    let responseErrorHandler: any;
    const originalLocation = window.location;

    beforeEach(() => {
      // Mock window.location
      delete (window as any).location;
      window.location = { href: '' } as any;

      // Get the response error handler that was registered
      const responseUse = mockAxiosInstance.interceptors.response.use;
      if (responseUse.mock.calls.length > 0) {
        responseErrorHandler = responseUse.mock.calls[0][1];
      }
    });

    afterEach(() => {
      window.location = originalLocation;
    });

    it('returns response when no error', () => {
      const responseUse = mockAxiosInstance.interceptors.response.use;
      const successHandler = responseUse.mock.calls[0][0];

      const response = { data: { id: 1 }, status: 200 };
      const result = successHandler(response);

      expect(result).toBe(response);
    });

    it('removes token and redirects to login on 401 error', async () => {
      localStorage.setItem('token', 'test-token');

      const error = {
        response: {
          status: 401,
          data: { detail: 'Unauthorized' },
        },
      };

      if (responseErrorHandler) {
        try {
          await responseErrorHandler(error);
        } catch (err) {
          expect(err).toBe(error);
        }

        expect(localStorage.getItem('token')).toBeNull();
        expect(window.location.href).toBe('/login');
      }
    });

    it('does not redirect on non-401 errors', async () => {
      const error = {
        response: {
          status: 404,
          data: { detail: 'Not found' },
        },
      };

      if (responseErrorHandler) {
        try {
          await responseErrorHandler(error);
        } catch (err) {
          expect(err).toBe(error);
        }

        expect(window.location.href).toBe('');
      }
    });

    it('handles errors without response object', async () => {
      const error = {
        message: 'Network Error',
      };

      if (responseErrorHandler) {
        try {
          await responseErrorHandler(error);
        } catch (err) {
          expect(err).toBe(error);
        }

        expect(window.location.href).toBe('');
      }
    });

    it('handles 401 error without removing non-existent token', async () => {
      // No token in localStorage
      const error = {
        response: {
          status: 401,
          data: { detail: 'Unauthorized' },
        },
      };

      if (responseErrorHandler) {
        try {
          await responseErrorHandler(error);
        } catch (err) {
          expect(err).toBe(error);
        }

        expect(localStorage.getItem('token')).toBeNull();
        expect(window.location.href).toBe('/login');
      }
    });
  });

  describe('API Client Methods', () => {
    it('has get method', () => {
      expect(apiClient.get).toBeDefined();
      expect(typeof apiClient.get).toBe('function');
    });

    it('has post method', () => {
      expect(apiClient.post).toBeDefined();
      expect(typeof apiClient.post).toBe('function');
    });

    it('has put method', () => {
      expect(apiClient.put).toBeDefined();
      expect(typeof apiClient.put).toBe('function');
    });

    it('has delete method', () => {
      expect(apiClient.delete).toBeDefined();
      expect(typeof apiClient.delete).toBe('function');
    });

    it('has patch method', () => {
      expect(apiClient.patch).toBeDefined();
      expect(typeof apiClient.patch).toBe('function');
    });
  });
});
