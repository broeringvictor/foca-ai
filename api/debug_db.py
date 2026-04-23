
import asyncio
from uuid import UUID
from sqlalchemy import select, func
from app.infrastructure.session import get_session
from app.infrastructure.model.study_note_model import StudyNoteModel
from app.infrastructure.model.question_model import QuestionModel

async def check_db():
    note_id = UUID("41b66043-5416-89f8-9303-da293cef907a")
    async for session in get_session():
        # Check Note
        note = await session.get(StudyNoteModel, note_id)
        if not note:
            print(f"Note {note_id} not found")
        else:
            has_emb = note.embedding is not None
            print(f"Note found. Has embedding: {has_emb}")
            if has_emb:
                 # Check first few elements of embedding to be sure
                 print(f"Embedding start: {note.embedding[:5] if isinstance(note.embedding, list) else 'not a list'}")

        # Check Questions count
        q_count = await session.execute(select(func.count(QuestionModel.id)))
        print(f"Total questions: {q_count.scalar()}")

        q_emb_count = await session.execute(select(func.count(QuestionModel.id)).where(QuestionModel.embedding.is_not(None)))
        print(f"Questions with embedding: {q_emb_count.scalar()}")
        
        break

if __name__ == "__main__":
    asyncio.run(check_db())
