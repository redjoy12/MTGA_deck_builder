import { mergeApplicationConfig, ApplicationConfig } from '@angular/core';
import { provideServerRendering } from '@angular/platform-server';
import { appConfig } from './app.config';
import { Actions } from '@ngrx/effects';
import { of } from 'rxjs';

const serverConfig: ApplicationConfig = {
  providers: [
    provideServerRendering(),
    { provide: Actions, useFactory: () => new Actions(of()) }
  ]
};

export const config = mergeApplicationConfig(appConfig, serverConfig);
