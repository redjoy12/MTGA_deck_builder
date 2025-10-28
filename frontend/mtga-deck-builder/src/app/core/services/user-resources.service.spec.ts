import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';

import { UserResourcesService } from './user-resources.service';

describe('UserResourcesService', () => {
  let service: UserResourcesService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });
    service = TestBed.inject(UserResourcesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
