export type RestConfigParams = {
  baseUrl: string;
};

export class RestConfig {
  public readonly baseUrl: string;

  constructor({ baseUrl }: RestConfigParams) {
    this.baseUrl = baseUrl;
  }
}
