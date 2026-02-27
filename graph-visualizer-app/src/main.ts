import {bootstrapApplication} from '@angular/platform-browser';
import {appConfig} from './app/app.config';
import {App} from './app/app';
import {RestConfigParams} from './app/rest/rest.config';
import {default as packageJson} from "../package.json";
import * as jsYaml from 'js-yaml';

bootstrapApplication(App, appConfig)
  .catch((err) => console.error(err));

export type Environment = {
  production: boolean;
  displayVersion: string;
  version: string;
  config: YamlConfig;
};

export type YamlConfig = {
  rest: RestConfigParams;
};

export const environment: Partial<Environment> = {
  production: false,
  version: packageJson.version
};

(async () => {
  const response = await fetch('./config/config.yaml');
  const yamlConfig = await response.text();
  environment.config = jsYaml.load(yamlConfig) as YamlConfig;

  bootstrapApplication(App, appConfig)
    .catch((err) => console.error(err));
})();
