import { Component, inject } from '@angular/core';
import { AbstractControl, FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);
  private toastr = inject(ToastrService);

  registerForm = this.fb.group({
    username: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
    confirmPassword: ['', Validators.required]
  }, { validators: this.passwordMatchValidator });

  private passwordMatchValidator(group: AbstractControl) {
    const password = group.get('password')?.value;
    const confirm = group.get('confirmPassword')?.value;
    return password === confirm ? null : { mismatch: true };
  }

  fieldInvalid(field: string): boolean {
    const ctrl = this.registerForm.get(field);
    return !!(ctrl && ctrl.invalid && ctrl.touched);
  }

  get passwordMismatch(): boolean {
    return this.registerForm.hasError('mismatch') && !!this.registerForm.get('confirmPassword')?.touched;
  }

  onSubmit() {
    if (this.registerForm.valid) {
      const { confirmPassword, ...data } = this.registerForm.value;
      this.authService.register(data).subscribe({
        next: () => {
          this.toastr.success('Registration successful. Please log in.');
          this.router.navigate(['/login']);
        },
        error: (err) => {
          this.toastr.error(err.error?.detail || 'Registration failed');
        }
      });
    }
  }
}
