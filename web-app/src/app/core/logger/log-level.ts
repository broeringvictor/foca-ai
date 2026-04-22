export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  OFF = 4
}

export interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  extra?: any[];
}
