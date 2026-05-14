export interface BalanceResponse {
  user_id: string;
  account_id: string;
  balance: number;
  currency: string;
  account_status: string;
}

export interface MovementItem {
  id: string;
  transfer_id: string;
  type: 'DEBITO' | 'CREDITO';
  amount: number;
  balance_after: number;
  created_at: string;
}

export interface MovementsResponse {
  user_id: string;
  account_id: string;
  total: number;
  page: number;
  page_size: number;
  movements: MovementItem[];
}

export interface TransferResponse {
  transfer_id: string;
  origin_account_id: string;
  destination_account_id: string;
  amount: number;
  status: string;
  message: string;
}

export interface ApiError {
  error_code: string;
  message: string;
  detail?: unknown;
}
