#!/usr/bin/env python3
"""
Script per cancellare eventi dal database
Uso: python3 delete_events.py
"""

import sys
from database import get_db, get_all_events, get_event_by_id

def list_events():
    """Elenca tutti gli eventi disponibili"""
    try:
        events = get_all_events()
        if not events:
            print("❌ Nessun evento trovato nel database.")
            return []
        
        print("\n📋 ELENCO EVENTI:")
        print("-" * 80)
        for event in events:
            visibility = "👁️ Visibile" if event['visible'] == 1 else "🙈 Nascosto"
            print(f"ID: {event['id']:3d} | {event['title']:30s} | {event['date']} | {visibility}")
        print("-" * 80)
        return events
    except Exception as e:
        print(f"❌ Errore nel caricamento degli eventi: {e}")
        return []

def delete_event(event_id):
    """Cancella un evento e tutte le sue prenotazioni"""
    try:
        event = get_event_by_id(event_id)
        if not event:
            print(f"❌ Evento con ID {event_id} non trovato.")
            return False
        
        # Conferma cancellazione
        print(f"\n⚠️  ATTENZIONE: Stai per cancellare l'evento:")
        print(f"   Titolo: {event['title']}")
        print(f"   Data: {event['date']}")
        print(f"   Questo eliminerà TUTTE le prenotazioni associate!")
        
        confirm = input("\nSei sicuro? Digita 'SI' per confermare: ").strip().upper()
        
        if confirm != 'SI':
            print("❌ Cancellazione annullata.")
            return False
        
        conn = get_db()
        
        # Cancella prima tutte le prenotazioni dell'evento
        conn.execute('DELETE FROM bookings WHERE event_id = ?', (event_id,))
        
        # Cancella poi l'evento
        conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Evento '{event['title']}' cancellato con successo!")
        return True
        
    except Exception as e:
        print(f"❌ Errore durante la cancellazione: {e}")
        return False

def delete_multiple_events(event_ids):
    """Cancella più eventi"""
    if not event_ids:
        print("❌ Nessun ID fornito.")
        return 0
    
    deleted_count = 0
    for event_id in event_ids:
        try:
            event_id = int(event_id)
            if delete_event(event_id):
                deleted_count += 1
            print()
        except ValueError:
            print(f"❌ '{event_id}' non è un ID valido.")
    
    return deleted_count

def main():
    """Funzione principale"""
    print("\n" + "="*80)
    print("🎭 CANCELLAZIONE EVENTI - Teatro San Raffaele")
    print("="*80)
    
    # Elenca gli eventi
    events = list_events()
    
    if not events:
        print("\nNessun evento da cancellare.")
        sys.exit(0)
    
    # Chiedi quali eventi cancellare
    print("\n📝 Inserisci gli ID degli eventi da cancellare (separati da virgole)")
    print("   Esempio: 1,3,5")
    print("   Oppure digita 'q' per uscire")
    
    user_input = input("\nID eventi: ").strip()
    
    if user_input.lower() == 'q':
        print("\n👋 Uscita.")
        sys.exit(0)
    
    # Parse gli ID
    try:
        event_ids = [id.strip() for id in user_input.split(',') if id.strip()]
    except Exception as e:
        print(f"❌ Errore nel parsing degli ID: {e}")
        sys.exit(1)
    
    if not event_ids:
        print("❌ Nessun ID fornito.")
        sys.exit(1)
    
    # Cancella gli eventi
    deleted = delete_multiple_events(event_ids)
    
    # Riepilogo
    print("\n" + "="*80)
    print(f"📊 Riepilogo: {deleted} evento/i cancellato/i con successo")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
