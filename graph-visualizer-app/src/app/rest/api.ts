import {ApiClient} from './api-client';

export abstract class Api {

  protected apiClient: ApiClient;

  protected constructor(client: ApiClient) {
    this.apiClient = client;
  }
}
