// frontend/src/services/tts/__mocks__/indexedDBMock.js
// Minimal IndexedDB mock for Vitest/Node.js
globalThis.IDBRequest = class {
  constructor() {
    this.result = null;
    this.error = null;
    this.onsuccess = null;
    this.onerror = null;
  }
};

class IDBObjectStore {
  constructor(store) {
    this._store = store;
  }
  put(value, key) {
    this._store[key] = value;
    const req = new IDBRequest();
    setTimeout(() => req.onsuccess && req.onsuccess({ target: req }), 0);
    return req;
  }
  get(key) {
    const req = new IDBRequest();
    setTimeout(() => {
      req.result = this._store[key];
      req.onsuccess && req.onsuccess({ target: req });
    }, 0);
    return req;
  }
  delete(key) {
    delete this._store[key];
    const req = new IDBRequest();
    setTimeout(() => req.onsuccess && req.onsuccess({ target: req }), 0);
    return req;
  }
  clear() {
    Object.keys(this._store).forEach(k => delete this._store[k]);
    const req = new IDBRequest();
    setTimeout(() => req.onsuccess && req.onsuccess({ target: req }), 0);
    return req;
  }
  createIndex() {}
}

class IDBTransaction {
  constructor(store) {
    this._store = store;
    this.oncomplete = null;
    this.onerror = null;
  }
  objectStore() {
    return new IDBObjectStore(this._store);
  }
}

class IDBDatabase {
  constructor(stores) {
    this._stores = stores;
    this.close = () => {};
  }
  transaction(storeName) {
    if (!this._stores[storeName]) this._stores[storeName] = {};
    return new IDBTransaction(this._stores[storeName]);
  }
  createObjectStore(storeName) {
    this._stores[storeName] = {};
    return new IDBObjectStore(this._stores[storeName]);
  }
}

const _dbs = {};

const indexedDBMock = {
  open(name, version) {
    const req = new IDBRequest();
    setTimeout(() => {
      if (!_dbs[name]) _dbs[name] = {};
      req.result = new IDBDatabase(_dbs[name]);
      req.onsuccess && req.onsuccess({ target: req });
    }, 0);
    return req;
  }
};

module.exports = indexedDBMock;
