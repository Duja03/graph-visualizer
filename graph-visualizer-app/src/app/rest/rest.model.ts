export interface ApiResponse<TResponse> {
  data: TResponse | null;
  headers: HttpHeaders;
}

export type HttpHeaders = {
  [key: string]: string | null;
};

export type RequestParamType = string | number | string[] | number[] | boolean;

export interface RequestConfig {
  headers?: RequestHeaders;
  params?: {

  };
  authenticated?: boolean;
}

export type ResponseType = 'arraybuffer' | 'blob' | 'json' | 'text';

export interface RequestHeaders {
  accept?: string;
  contentType?: string;
  responseType?: ResponseType;
  otherHeaders?: Record<string, string>;
}

export interface MultiPart {
  name: string;
  content: string | File;
}

export interface Page<Content> {
  content: Content[];
  pageable: Pageable;
  totalPages: number;
  totalElements: number;
  last: boolean;
  size: boolean;
  number: number;
  sort: Sort;
  first: boolean;
  numberOfElements: number;
  empty: boolean;
}

export interface Pageable {
  sort: Sort;
  pageNumber: number;
  pageSize: number;
  offset: number;
  paged: boolean;
  unpaged: boolean;
}

export interface Sort {
  sorted: boolean;
  unsorted: boolean;
  empty: boolean;
}

export type PageParameters = {
  page?: number;
  size?: number;
  sort?: string | string[];
};
