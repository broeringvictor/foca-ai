import { Injectable, isDevMode } from '@angular/core';
import { LogEntry, LogLevel } from './log-level';

@Injectable({
  providedIn: 'root',
})
export class LoggerService {
  // Define o nível mínimo de log. Em produção, poderíamos subir para WARN.
  private level: LogLevel = isDevMode() ? LogLevel.DEBUG : LogLevel.INFO;

  debug(message: string, ...extra: any[]) {
    this.log(LogLevel.DEBUG, message, extra);
  }

  info(message: string, ...extra: any[]) {
    this.log(LogLevel.INFO, message, extra);
  }

  warn(message: string, ...extra: any[]) {
    this.log(LogLevel.WARN, message, extra);
  }

  error(message: string, ...extra: any[]) {
    this.log(LogLevel.ERROR, message, extra);
  }

  private log(level: LogLevel, message: string, extra: any[]) {
    if (this.shouldLog(level)) {
      const entry: LogEntry = {
        level,
        message,
        timestamp: new Date().toISOString(),
        extra,
      };

      this.writeToConsole(entry);

      // Aqui poderíamos enviar o log para um servidor externo (ex: Sentry)
      // if (level >= LogLevel.ERROR) { this.sendToRemoteServer(entry); }
    }
  }

  private shouldLog(level: LogLevel): boolean {
    return level >= this.level;
  }

  private writeToConsole(entry: LogEntry) {
    const format = `[${entry.timestamp}] [${LogLevel[entry.level]}] ${entry.message}`;

    switch (entry.level) {
      case LogLevel.DEBUG:
        console.debug(format, ...entry.extra!);
        break;
      case LogLevel.INFO:
        console.info(format, ...entry.extra!);
        break;
      case LogLevel.WARN:
        console.warn(format, ...entry.extra!);
        break;
      case LogLevel.ERROR:
        console.error(format, ...entry.extra!);
        break;
    }
  }
}
