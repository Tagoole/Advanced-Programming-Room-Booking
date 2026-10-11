# Meeting Room Booking

Domain model for booking meeting rooms, organised using Clean Architecture.
Two aggregates, Booking and Room, connected by the BookingConfirmed event.

## Running

Needs Python 3.10+ and pytest.

    pip install pytest

From inside `meeting_room_booking/`:

    pytest tests/ -v      # all 8 tests
    python main.py        # walks both use cases and the three refusals

## Layout

    domain/           entities, value objects, aggregates, domain service, events
    application/      use cases, DTOs, repository interfaces, event handlers
    infrastructure/   in-memory repositories
    main.py           entry point
    tests/            T1-T8

Dependencies only point inwards. `domain/` imports nothing outside itself and
`application/` never imports `infrastructure/` - the concrete repositories
implement interfaces declared in `application/` and get passed in from
`main.py`.

## Tests

| Test | Covers |
|------|--------|
| T1 | valid time range, plus the 18:00 boundary |
| T2 | booking keeps its reference across a state change, refuses a second confirm |
| T3 | room refuses an overlapping booking |
| T4 | capacity check, exactly-full boundary |
| T5 | confirming raises BookingConfirmed |
| T6 | confirm stops if the room was never saved |
| T7 | full confirm flow, room updated by the event handler |
| T8 | room refuses the follow-up, nothing is persisted |

`docs/tdd-evidence.md` has the fail-then-pass cycle for T6, with the raw
pytest output in `docs/`.

## AI use
Claude was used to review the project against the coursework brief and the
course texts. It identified a missing output DTO