import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

// PrimeNG modules
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { ButtonModule } from 'primeng/button';
import { MessageModule } from 'primeng/message';
import { MessagesModule } from 'primeng/messages';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    CardModule,
    InputTextModule,
    PasswordModule,
    ButtonModule,
    MessageModule,
    MessagesModule
  ],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
  loading = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // If already authenticated, redirect to deck creator
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/deck-creator']);
    }

    // Initialize register form with validation
    this.registerForm = this.formBuilder.group({
      username: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8), this.passwordStrengthValidator]],
      confirmPassword: ['', [Validators.required]]
    }, {
      validators: this.passwordMatchValidator
    });
  }

  // Custom validator for password strength
  passwordStrengthValidator(control: AbstractControl): ValidationErrors | null {
    const value = control.value;
    if (!value) {
      return null;
    }

    const hasLetter = /[a-zA-Z]/.test(value);
    const hasNumber = /[0-9]/.test(value);

    const passwordValid = hasLetter && hasNumber;

    return passwordValid ? null : { passwordStrength: true };
  }

  // Custom validator to check if passwords match
  passwordMatchValidator(group: AbstractControl): ValidationErrors | null {
    const password = group.get('password')?.value;
    const confirmPassword = group.get('confirmPassword')?.value;

    return password === confirmPassword ? null : { passwordMismatch: true };
  }

  // Convenience getter for form controls
  get f() {
    return this.registerForm.controls;
  }

  onSubmit(): void {
    // Clear previous messages
    this.errorMessage = '';
    this.successMessage = '';

    // Check if form is valid
    if (this.registerForm.invalid) {
      // Mark all fields as touched to show validation errors
      Object.keys(this.registerForm.controls).forEach(key => {
        this.registerForm.get(key)?.markAsTouched();
      });
      return;
    }

    // Set loading state
    this.loading = true;

    // Extract registration data (exclude confirmPassword)
    const { username, email, password } = this.registerForm.value;

    // Attempt registration
    this.authService.register({ username, email, password }).subscribe({
      next: () => {
        // Registration successful
        this.loading = false;
        this.successMessage = 'Registration successful! Redirecting to login...';

        // Redirect to login after 2 seconds
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      },
      error: (error) => {
        // Registration failed, display error message
        this.loading = false;
        this.errorMessage = error?.error?.detail || error?.message || 'Registration failed. Please try again.';
      }
    });
  }

  // Get error message for username field
  getUsernameError(): string {
    const username = this.registerForm.get('username');
    if (username?.hasError('required') && username?.touched) {
      return 'Username is required';
    }
    if (username?.hasError('minlength') && username?.touched) {
      return 'Username must be at least 3 characters';
    }
    if (username?.hasError('maxlength') && username?.touched) {
      return 'Username must not exceed 50 characters';
    }
    return '';
  }

  // Get error message for email field
  getEmailError(): string {
    const email = this.registerForm.get('email');
    if (email?.hasError('required') && email?.touched) {
      return 'Email is required';
    }
    if (email?.hasError('email') && email?.touched) {
      return 'Please enter a valid email address';
    }
    return '';
  }

  // Get error message for password field
  getPasswordError(): string {
    const password = this.registerForm.get('password');
    if (password?.hasError('required') && password?.touched) {
      return 'Password is required';
    }
    if (password?.hasError('minlength') && password?.touched) {
      return 'Password must be at least 8 characters';
    }
    if (password?.hasError('passwordStrength') && password?.touched) {
      return 'Password must contain at least one letter and one digit';
    }
    return '';
  }

  // Get error message for confirm password field
  getConfirmPasswordError(): string {
    const confirmPassword = this.registerForm.get('confirmPassword');
    if (confirmPassword?.hasError('required') && confirmPassword?.touched) {
      return 'Please confirm your password';
    }
    if (this.registerForm.hasError('passwordMismatch') && confirmPassword?.touched) {
      return 'Passwords do not match';
    }
    return '';
  }
}
