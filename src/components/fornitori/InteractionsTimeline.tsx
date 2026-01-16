// ═══════════════════════════════════════════════════════════════════
// FLUXION - Supplier Interactions Timeline
// Shows communication history with a supplier
// ═══════════════════════════════════════════════════════════════════

import { type FC } from 'react';
import { Mail, MessageCircle, Phone, StickyNote, CheckCircle, XCircle, Clock } from 'lucide-react';
import type { SupplierInteraction } from '@/types/supplier';

interface InteractionsTimelineProps {
  interactions: SupplierInteraction[];
  orderNumbers?: Record<string, string>;
}

const INTERACTION_ICONS = {
  email: Mail,
  whatsapp: MessageCircle,
  call: Phone,
  note: StickyNote,
};

const INTERACTION_COLORS = {
  email: 'bg-cyan-500',
  whatsapp: 'bg-green-500',
  call: 'bg-purple-500',
  note: 'bg-yellow-500',
};

const STATUS_ICONS = {
  sent: Clock,
  delivered: CheckCircle,
  read: CheckCircle,
  failed: XCircle,
};

export const InteractionsTimeline: FC<InteractionsTimelineProps> = ({
  interactions,
  orderNumbers = {},
}) => {
  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getInteractionLabel = (tipo: SupplierInteraction['tipo']) => {
    switch (tipo) {
      case 'email':
        return 'Email';
      case 'whatsapp':
        return 'WhatsApp';
      case 'call':
        return 'Chiamata';
      case 'note':
        return 'Nota';
      default:
        return tipo;
    }
  };

  if (interactions.length === 0) {
    return (
      <div className="text-center py-8 text-slate-400">
        <MessageCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
        <p>Nessuna interazione registrata</p>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-700" />

      {/* Timeline items */}
      <div className="space-y-4">
        {interactions.map((interaction) => {
          const Icon = INTERACTION_ICONS[interaction.tipo] || StickyNote;
          const colorClass = INTERACTION_COLORS[interaction.tipo] || 'bg-slate-500';
          const StatusIcon = interaction.status ? STATUS_ICONS[interaction.status as keyof typeof STATUS_ICONS] : null;

          return (
            <div key={interaction.id} className="relative flex gap-4 pl-10">
              {/* Icon */}
              <div
                className={`absolute left-0 w-8 h-8 rounded-full ${colorClass} flex items-center justify-center`}
              >
                <Icon className="h-4 w-4 text-white" />
              </div>

              {/* Content */}
              <div className="flex-1 bg-slate-900 border border-slate-800 rounded-lg p-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="font-medium text-white">
                      {getInteractionLabel(interaction.tipo)}
                    </span>
                    {interaction.order_id && orderNumbers[interaction.order_id] && (
                      <span className="ml-2 text-xs text-slate-400 font-mono">
                        ({orderNumbers[interaction.order_id]})
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    {StatusIcon && interaction.status && (
                      <span
                        className={`flex items-center gap-1 ${
                          interaction.status === 'failed' ? 'text-red-400' : 'text-green-400'
                        }`}
                      >
                        <StatusIcon className="h-3 w-3" />
                        {interaction.status}
                      </span>
                    )}
                    <span>{formatDateTime(interaction.created_at)}</span>
                  </div>
                </div>

                {interaction.messaggio && (
                  <p className="mt-2 text-sm text-slate-300 whitespace-pre-wrap">
                    {interaction.messaggio}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
