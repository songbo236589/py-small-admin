// 存储选项接口
export interface StorageOptions {
  prefix?: string; // 键名前缀
  expire?: number; // 过期时间（秒）
}

// Token 存储接口
export interface TokenStorage {
  accessToken: string;
  refreshToken: string;
  expiresAt?: string;
  refreshExpiresAt?: string;
}

// 存储数据内部结构（包含过期时间）
interface StorageData<T> {
  value: T;
  expire?: number; // 过期时间戳
}

/**
 * localStorage 工具类
 * 提供类型安全的 localStorage 操作方法
 */
class LocalStorageUtils {
  private readonly defaultPrefix = 'app_';

  /**
   * 获取完整的键名
   * @param key 原始键名
   * @param prefix 前缀
   * @returns 完整键名
   */
  private getKey(key: string, prefix?: string): string {
    const actualPrefix = prefix || this.defaultPrefix;
    return `${actualPrefix}${key}`;
  }

  /**
   * 检查 localStorage 是否可用
   * @returns 是否可用
   */
  private isAvailable(): boolean {
    try {
      const testKey = '__test__';
      localStorage.setItem(testKey, 'test');
      localStorage.removeItem(testKey);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * 获取存储数据
   * @param key 键名
   * @param defaultValue 默认值
   * @returns 存储的值或默认值
   */
  get<T>(key: string, defaultValue?: T): T | null {
    if (!this.isAvailable()) {
      return defaultValue || null;
    }

    try {
      const fullKey = this.getKey(key);
      const item = localStorage.getItem(fullKey);

      if (!item) {
        return defaultValue || null;
      }

      const data: StorageData<T> = JSON.parse(item);

      // 检查是否过期
      if (data.expire && Date.now() > data.expire) {
        this.remove(key);
        return defaultValue || null;
      }

      return data.value;
    } catch {
      return defaultValue || null;
    }
  }

  /**
   * 设置存储数据
   * @param key 键名
   * @param value 值
   * @param options 选项
   */
  set<T>(key: string, value: T, options?: StorageOptions): void {
    if (!this.isAvailable()) {
      console.warn('localStorage is not available');
      return;
    }

    try {
      const fullKey = this.getKey(key, options?.prefix);
      const data: StorageData<T> = {
        value,
      };

      // 设置过期时间
      if (options?.expire) {
        data.expire = Date.now() + options.expire * 1000;
      }

      localStorage.setItem(fullKey, JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  }

  /**
   * 移除存储数据
   * @param key 键名
   */
  remove(key: string): void {
    if (!this.isAvailable()) {
      return;
    }

    try {
      const fullKey = this.getKey(key);
      localStorage.removeItem(fullKey);
    } catch (error) {
      console.error('Failed to remove from localStorage:', error);
    }
  }

  /**
   * 清空所有存储数据（仅清除带前缀的）
   * @param prefix 前缀，默认为应用前缀
   */
  clear(prefix?: string): void {
    if (!this.isAvailable()) {
      return;
    }

    try {
      const actualPrefix = prefix || this.defaultPrefix;
      const keys = Object.keys(localStorage);

      keys.forEach((key) => {
        if (key.startsWith(actualPrefix)) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.error('Failed to clear localStorage:', error);
    }
  }

  /**
   * 检查数据是否过期
   * @param key 键名
   * @returns 是否过期
   */
  isExpired(key: string): boolean {
    if (!this.isAvailable()) {
      return true;
    }

    try {
      const fullKey = this.getKey(key);
      const item = localStorage.getItem(fullKey);

      if (!item) {
        return true;
      }

      const data: StorageData<any> = JSON.parse(item);

      if (!data.expire) {
        return false;
      }

      return Date.now() > data.expire;
    } catch {
      return true;
    }
  }

  /**
   * 获取所有键名（仅返回带前缀的）
   * @param prefix 前缀，默认为应用前缀
   * @returns 键名数组
   */
  getAllKeys(prefix?: string): string[] {
    if (!this.isAvailable()) {
      return [];
    }

    try {
      const actualPrefix = prefix || this.defaultPrefix;
      const keys = Object.keys(localStorage);

      return keys
        .filter((key) => key.startsWith(actualPrefix))
        .map((key) => key.replace(actualPrefix, ''));
    } catch {
      return [];
    }
  }

  /**
   * 获取存储大小（字节）
   * @returns 存储大小
   */
  getStorageSize(): number {
    if (!this.isAvailable()) {
      return 0;
    }

    try {
      let totalSize = 0;
      const keys = Object.keys(localStorage);

      keys.forEach((key) => {
        const value = localStorage.getItem(key);
        if (value) {
          totalSize += new Blob([key + value]).size;
        }
      });

      return totalSize;
    } catch {
      return 0;
    }
  }
}

// 创建并导出单例实例
const storage = new LocalStorageUtils();
export default storage;

// 导出类型定义
export type { LocalStorageUtils };
