import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
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
  selector: 'app-login',
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
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  loading = false;
  errorMessage = '';

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

    // Initialize login form with validation
    this.loginForm = this.formBuilder.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(8)]]
    });
  }

  // Convenience getter for form controls
  get f() {
    return this.loginForm.controls;
  }

  onSubmit(): void {
    // Clear previous error message
    this.errorMessage = '';

    // Check if form is valid
    if (this.loginForm.invalid) {
      // Mark all fields as touched to show validation errors
      Object.keys(this.loginForm.controls).forEach(key => {
        this.loginForm.get(key)?.markAsTouched();
      });
      return;
    }

    // Set loading state
    this.loading = true;

    // Attempt login
    this.authService.login(this.loginForm.value).subscribe({
      next: (user) => {
        // Login successful, redirect to deck creator
        this.router.navigate(['/deck-creator']);
      },
      error: (error) => {
        // Login failed, display error message
        this.loading = false;
        this.errorMessage = error?.error?.detail || error?.message || 'Login failed. Please check your credentials.';
      }
    });
  }

  // Get error message for username field
  getUsernameError(): string {
    const username = this.loginForm.get('username');
    if (username?.hasError('required') && username?.touched) {
      return 'Username is required';
    }
    if (username?.hasError('minlength') && username?.touched) {
      return 'Username must be at least 3 characters';
    }
    return '';
  }

  // Get error message for password field
  getPasswordError(): string {
    const password = this.loginForm.get('password');
    if (password?.hasError('required') && password?.touched) {
      return 'Password is required';
    }
    if (password?.hasError('minlength') && password?.touched) {
      return 'Password must be at least 8 characters';
    }
    return '';
  }
}
