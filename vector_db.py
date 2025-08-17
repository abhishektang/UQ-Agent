# vector_db.py
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import json


def initialize_vector_db():
    client = chromadb.PersistentClient(path="./chroma_db")
    # Delete the existing collection if it exists
    try:
        client.delete_collection("navigation_examples")
    except:
        pass  # Collection didn't exist
    collection = client.get_or_create_collection(
        name="navigation_examples",
        metadata={"hnsw:space": "cosine"}
    )

    # Initialize the vector DB with examples
    db = ExampleVectorDB(collection)
    db.add_examples(get_examples())
    return db


class ExampleVectorDB:
    def __init__(self, collection):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = collection
        self.examples = []

    def add_examples(self, examples: List[Dict]):
        """Add examples to the vector database"""
        self.examples = examples.copy()

        texts = [ex["query"] for ex in examples]
        embeddings = self.encoder.encode(texts).tolist()
        ids = [str(i) for i in range(len(texts))]
        metadatas = [{"plan": json.dumps(ex["plan"])} for ex in examples]

        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    def get_similar_examples(self, query: str, k: int = 3) -> List[Dict]:
        """Retrieve k most similar examples"""
        query_embedding = self.encoder.encode([query]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            include=["metadatas", "documents"]
        )

        similar_examples = []
        for i in range(len(results["ids"][0])):
            similar_examples.append({
                "query": results["documents"][0][i],
                "plan": json.loads(results["metadatas"][0][i]["plan"])
            })

        return similar_examples

    # Initialize with your existing examples
def get_examples():
    # Your existing examples
    return [
        {
            "query": "check nursing announcements",
            "plan": {
                "steps": [
                    {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                    {"action": "click", "element_description": "Nursing"},
                    {"action": "click", "element_description": "Announcements"}
                ]
            }
        },

{
    "query": "Show me updates for Software Engineering",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Software Engineering"},
            {"action": "click", "element_description": "Announcements"}
        ]
    }
},
{
    "query": "Has the lecturer posted anything new in DECO7250?",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Human-Computer Interaction"},
            {"action": "click", "element_description": "Announcements"}
        ]
    }
},
{
    "query": "Check if there are updates for ENGG1000",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Introduction To Professional Engineering"},
            {"action": "click", "element_description": "Announcements"}
        ]
    }
},
{
    "query": "What's new in Introduction to Professional Engineering?",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Professional Engineering"},
            {"action": "click", "element_description": "Announcements"}
        ]
    }
},
{
    "query": "Need to see if there are new posts for STAT1201",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Analysis of Scientific Data"},
            {"action": "click", "element_description": "Announcements"}
        ]
    }
},

{
    "query": "Looking for updates in Foundations of Healthcare",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Foundations of Healthcare"},
            {"action": "click", "element_description": "Announcements"}
        ]
    }
},

{
    "query": "Check if there are new announcements for WRIT1001",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Writing for International Students"},
            {"action": "click", "element_description": "Announcements"}
        ]
    }
},

{
        "query": "check announcements for COMP3702 - Artificial Intelligence",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Artificial Intelligence"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "AI course updates pls",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Artificial Intelligence"},
                {"action": "click", "element_description": "Announcements"}  # Intentional typo in element
            ]
        }
    },
    {
        "query": "machine learning announcement?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},  # Intentional URL typo
                {"action": "click", "element_description": "Machine Learning"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },




    # Science (with variations)
    {
        "query": "PHYS1171 announcments",  # Misspelling
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Physical Basis of Biological Systems"},  # Intentional typo
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "physics for engineers updates",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Physics"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },

    {
        "query": "see DECO7250 announcemnt",  # Typo
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Human-Computer Interaction"},
                {"action": "click", "element_description": "Anouncements"}  # Typo
            ]
        }
    },
{
        "query": "see Research and Methods announcemnt",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Research Methods"},
                {"action": "click", "element_description": "Anouncements"}  # Typo
            ]
        }
    },
    # Computer Science
    {
        "query": "COMP3506 announcements",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Algorithms and Data Structures"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "Show me CSSE3200 updates",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Software Engineering Studio: Design, Implement and Test"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "View the course outline for COMP2041",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Theory of Computing"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Display the syllabus for Software Engineering",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Software Engineering"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "I need to see the course details for DECO7250",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Human-Computer Interaction"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Where can I find the ENGG1000 course profile?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Introduction to Professional Engineering"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Access the outline for Introduction to Engineering",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Introduction to Engineering"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "I want to check the BISM1201 course structure",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Transforming Business with Information Systems"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "I need to access the STAT1201 course profile",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Analysis of Scientific Data"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Open the COMP2041 course profile",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Theory of Computing"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "I need to view the Software Engineering course profile",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Software Engineering"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Where can I find the DECO7250 course profile?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Human-Computer Interaction"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Show me the ENGG1000 course profile",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Introduction to Professional Engineering"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Display the Introduction to Engineering course profile",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Introduction to Engineering"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },

    {
        "query": "COMP3702 Artificial Intelligence course profile",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Artificial Intelligence"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Show AI course profile",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Artificial Intelligence"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Show me COMP3710 course profile",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Pattern Recognition and Analysis"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "View course outline for Pattern Recognition",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Pattern Recognition and Analysis"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Access REIT4882 course profile",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Computing Research Project"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Show Research and Development Methods course outline",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Computing Research Project"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Open REIT4842 profile",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Research and Development Methods and Practice"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Display Research Methods syllabus for REIT4842",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Research and Development Methods and Practice"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Access REIT7842 course outline",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Research and Development Methods and Practice"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Show me the Research Methods content for REIT7842",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Research and Development Methods and Practice"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "View REIT4882 course details",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Computing Research Project"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Where can I find the Research Methods outline for REIT4882?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Computing Research Project"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Open DECO3801 profile",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Design Computing Studio 3 - Build"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Show Design Computing Studio 3 syllabus",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Design Computing Studio 3 - Build"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Access DECO3800 course outline",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Design Computing Studio 3 - Proposal"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Show me the Design Computing Studio 3 - Proposal profile",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Design Computing Studio 3 - Proposal"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },
    {
        "query": "Check COMP3710 announcements",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Pattern Recognition and Analysis"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "Any updates for Pattern Recognition course?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Pattern Recognition and Analysis"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "REIT4882 announcements please",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Computing Research Project"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "Any new posts for Research and Development Methods?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Computing Research Project"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "Check REIT4842 announcements",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Research and Development Methods and Practice"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "Any updates in Research Methods (REIT4842)?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Research and Development Methods and Practice"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "REIT7842 notifications please",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Research and Development Methods and Practice"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "Has there been any new information posted for REIT7842 Research Methods?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Research and Development Methods and Practice"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "REIT4882 latest updates",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Computing Research Project"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "Are there new posts for Research Methods in REIT4882?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Computing Research Project"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "Check DECO3801 announcements",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Design Computing Studio 3 - Build"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "Any updates for Design Computing Studio 3?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Design Computing Studio 3 - Build"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "DECO3800 announcements please",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Design Computing Studio 3 - Proposal"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "Has there been any new information posted for Design Computing Studio 3?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Design Computing Studio 3 - Proposal"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "Has there been any new information posted for Design Computing Studio 3?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Design Computing Studio 3 - Proposal"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }

    },
    {
        "query": "Open Timetable",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
                {"action": "click", "element_description": "My Timetable"},
                {"action": "click", "element_description": "Timetable"},
            ]
        }

    },
    {
    "query": "Show my full timetable",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
                {"action": "click", "element_description": "My Timetable"},
                {"action": "click", "element_description": "Timetable"},
        ]
    }
},
{
    "query": "Open my schedule for this week",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
                {"action": "click", "element_description": "My Timetable"},
                {"action": "click", "element_description": "Timetable"},
        ]
    }
},
{
    "query": "Display timetable showing all my enrolled courses",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
                {"action": "click", "element_description": "My Timetable"},
                {"action": "click", "element_description": "Timetable"},
        ]
    }
},
{
    "query": "Check my grades",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
                {"action": "click", "element_description": "mySI-net"},
                {"action": "click", "element_description": "Enrolments"},
                {"action": "click", "element_description": "Study Report"},
                {"action": "click", "element_description": "Studies Report"},
        ]
    }
},{
"query": "GRADES",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
                {"action": "click", "element_description": "mySI-net"},
                {"action": "click", "element_description": "Enrolments"},
                {"action": "click", "element_description": "Study Report"},
                {"action": "click", "element_description": "Studies Report"},
        ]
    }
},
{
    "query": "Display my academic results",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "mySI-net"},
            {"action": "click", "element_description": "Enrolments"},
            {"action": "click", "element_description": "Study Report"},
            {"action": "click", "element_description": "Studies Report"}
        ]
    }
},
{
    "query": "Show me my marks",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "mySI-net"},
            {"action": "click", "element_description": "Enrolments"},
            {"action": "click", "element_description": "Study Report"},
            {"action": "click", "element_description": "Studies Report"}
        ]
    }
},
{
    "query": "What are my course results?",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "mySI-net"},
            {"action": "click", "element_description": "Enrolments"},
            {"action": "click", "element_description": "Study Report"},
            {"action": "click", "element_description": "Studies Report"}
        ]
    }
},
{
    "query": "How am I performing academically?",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "mySI-net"},
            {"action": "click", "element_description": "Enrolments"},
            {"action": "click", "element_description": "Study Report"},
            {"action": "click", "element_description": "Studies Report"}
        ]
    }
},
{
    "query": "I want to see my scores",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "mySI-net"},
            {"action": "click", "element_description": "Enrolments"},
            {"action": "click", "element_description": "Study Report"},
            {"action": "click", "element_description": "Studies Report"}
        ]
    }
},{
"query": "To check my grades",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "mySI-net"},
            {"action": "click", "element_description": "Enrolments"},
            {"action": "click", "element_description": "Study Report"},
            {"action": "click", "element_description": "Studies Report"}
        ]
    }
},
{
"query": "Grades",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "mySI-net"},
            {"action": "click", "element_description": "Enrolments"},
            {"action": "click", "element_description": "Study Report"},
            {"action": "click", "element_description": "Studies Report"}
        ]
    }
},



]