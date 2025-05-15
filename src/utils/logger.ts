
export class Logger {
  private context: string;

  constructor(context: string = 'App') {
    this.context = context;
  }

  info(message: string, ...args: any[]) {
    // eslint-disable-next-line no-console
    console.info(`[INFO] [${this.context}]`, message, ...args);
  }

  warn(message: string, ...args: any[]) {
    // eslint-disable-next-line no-console
    console.warn(`[WARN] [${this.context}]`, message, ...args);
  }

  error(message: string, ...args: any[]) {
    // eslint-disable-next-line no-console
    console.error(`[ERROR] [${this.context}]`, message, ...args);
  }
}
