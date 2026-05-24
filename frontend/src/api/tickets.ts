import { api } from './client';
import type { Ticket, TicketCreate } from '../types';

export async function getTickets(): Promise<Ticket[]> {
  return api.get<Ticket[]>('/tickets');
}

export async function getTicket(id: number): Promise<Ticket> {
  return api.get<Ticket>(`/tickets/${id}`);
}

export async function createTicket(data: TicketCreate): Promise<Ticket> {
  return api.post<Ticket>('/tickets', data);
}

export async function submitTicket(data: TicketCreate): Promise<Ticket> {
  return api.post<Ticket>('/tickets/submit', data);
}
