import { Component, ChangeDetectionStrategy, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { form, submit, required, email, minLength, validate, FormField } from '@angular/forms/signals';
import { MessageService } from 'primeng/api';
import { Card } from 'primeng/card';
import { Tabs, TabList, Tab, TabPanels, TabPanel } from 'primeng/tabs';
import { InputText } from 'primeng/inputtext';
import { Button } from 'primeng/button';
import { Toast } from 'primeng/toast';
import { AuthService } from '../../core/auth/auth.service';
import { UsersService } from '../../core/auth/users.service';
import { RegisterDTO } from '../../core/models/api.models';

interface RegisterFormModel {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  password_confirm: string;
}

@Component({
  standalone: true,
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [Card, Tabs, TabList, Tab, TabPanels, TabPanel, InputText, Button, Toast, FormField],
})
export class AuthComponent {
  private router = inject(Router);
  private authService = inject(AuthService);
  private usersService = inject(UsersService);
  private messageService = inject(MessageService);

  activeTab = signal<string | number | undefined>('login');

  loginModel = signal({ email: '', password: '' });
  loginForm = form(this.loginModel, (s) => {
    required(s.email);
    email(s.email, { message: 'E-mail inválido' });
    required(s.password, { message: 'Senha obrigatória' });
  });

  registerModel = signal<RegisterFormModel>({
    first_name: '', last_name: '', email: '', password: '', password_confirm: '',
  });
  registerForm = form(this.registerModel, (s) => {
    required(s.first_name, { message: 'Nome obrigatório' });
    required(s.last_name, { message: 'Sobrenome obrigatório' });
    required(s.email);
    email(s.email, { message: 'E-mail inválido' });
    required(s.password, { message: 'Senha obrigatória' });
    minLength(s.password, 8, { message: 'Mínimo 8 caracteres' });
    required(s.password_confirm, { message: 'Confirme a senha' });
    validate(s.password_confirm, () => {
      const m = this.registerModel();
      if (m.password_confirm !== m.password) {
        return { kind: 'match', message: 'As senhas não coincidem' };
      }
      return undefined;
    });
  });

  async onLoginSubmit() {
    await submit(this.loginForm, async () => {
      try {
        await firstValueFrom(this.authService.login(this.loginModel()));
        this.router.navigate(['/study-notes']);
      } catch (err: any) {
        const msg = err?.error?.detail?.[0]?.message ?? err?.message ?? 'Credenciais inválidas';
        this.messageService.add({ severity: 'error', summary: 'Erro', detail: msg, life: 4000 });
      }
    });
  }

  async onRegisterSubmit() {
    await submit(this.registerForm, async () => {
      try {
        const { password_confirm: _, ...dto } = this.registerModel();
        await firstValueFrom(this.usersService.register(dto as RegisterDTO));
        this.messageService.add({
          severity: 'success', summary: 'Conta criada!',
          detail: 'Faça login para continuar.', life: 4000,
        });
        this.activeTab.set('login');
      } catch (err: any) {
        const msg = err?.message ?? 'Erro ao criar conta';
        this.messageService.add({ severity: 'error', summary: 'Erro', detail: msg, life: 4000 });
      }
    });
  }
}
