// Type definitions for vitest global variables
declare global {
  const vi: {
    fn: () => any;
    mock: (moduleName: string) => any;
    spyOn: (object: any, method: string) => any;
  };
}

export {}; // Convert this file to a module
