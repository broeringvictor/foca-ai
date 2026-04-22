import { ErrorHandler, Injectable, inject } from '@angular/core';
import { LoggerService } from './logger.service';

@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  private logger = inject(LoggerService);

  handleError(error: any): void {
    // Aqui capturamos o erro e o logamos com detalhes.
    this.logger.error('Unhandled Exception:', error);

    // Se houver stack trace, podemos extrair informações adicionais aqui
    // const message = error.message ? error.message : error.toString();
    // const stack = error.stack ? error.stack : '';

    // Lançamos o erro novamente se for necessário para depuração nativa (opcional)
    // throw error;
  }
}
