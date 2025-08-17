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
        "query": "COMP3710 announcements",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Pattern Recognition and Analysis"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "any new posts in pattern recog course?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Pattern Recognition and Analysis"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "updates DECO3801",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Design Computing Studio 3"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "Design Comp Studio 3 announcement?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Design Computing Studio 3"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "see R&D methods announcemnt",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Research and Development Methods"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "research and development methods update pls",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Research and Development Methods"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "check announcements COMP3400",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Functional and Logical Programming"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "F&L programming updates?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Functional and Logical Programming"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "DECO3800 proposal announcement?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Design Computing Studio 3 - Proposal"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "Design Comp Studio proposal updates",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Design Computing Studio 3 - Proposal"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "ENGG1300 updates?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Introduction to Electrical Systems"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
    {
        "query": "any announcemnt for Intro Elec Sys?",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Introduction to Electrical Systems"},
                {"action": "click", "element_description": "Announcements"}
            ]
        }
    },
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
        "query": "I need to see the course details for DECO2500",
        "plan": {
            "steps": [
                {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Human-Computer Interaction"},
                {"action": "click", "element_description": "Course Profile"},
                {"action": "click", "element_description": "View Profile"}
            ]
        }
    },{
    "query": "Show Artificial Intelligence course details",
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
    "query": "Show COMP2041",
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
    "query": "Artificial Intelligence syllabus",
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
    "query": "List all my courses",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"}
        ]
    }
},
{
    "query": "Show me all my enrolled courses",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"}
        ]
    }
},
{
    "query": "Display my course list",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"}
        ]
    }
},
{
    "query": "Open all my courses",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"}
        ]
    }
},
{
    "query": "View courses I am enrolled in",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"}
        ]
    }
},
{
    "query": "Check my current courses",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"}
        ]
    }
},
{
    "query": "List my subjects this semester",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"}
        ]
    }
},
{
    "query": "Show enrolled subjects",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"}
        ]
    }
},
{
    "query": "Open my current subject list",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"}
        ]
    }
},
{
    "query": "Open AI course",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"}
        ]
    }
},
{
    "query": "View COMP3702",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"}
        ]
    }
},
{
    "query": "Go to Artificial Intelligence",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"}
        ]
    }
},
{
    "query": "Show AI syllabus",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"}
        ]
    }
},
{
    "query": "Open Software Engineering",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Software Engineering"}
        ]
    }
},
{
    "query": "View BISM1201",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Transforming Business with Information Systems"}
        ]
    }
},
{
    "query": "Open STAT1201 course",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Analysis of Scientific Data"}
        ]
    }
},
{
    "query": "Go to ENGG1000",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Introduction to Professional Engineering"}
        ]
    }
},
{
    "query": "Open Introduction to Engineering",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Introduction to Engineering"}
        ]
    }
},
{
    "query": "Open DECO2500",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Human-Computer Interaction"}
        ]
    }
},
{
    "query": "View DECO3800",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Design Computing Studio 3 - Proposal"}
        ]
    }
},
{
    "query": "Open DECO3801",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Design Computing Studio 3 - Build"}
        ]
    }
},
{
    "query": "Access REIT4882",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Computing Research Project"}
        ]
    }
},
{
    "query": "Open REIT4842",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Research and Development Methods and Practice"}
        ]
    }
},
{
    "query": "View REIT7842",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Research and Development Methods and Practice"}
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
    "query": "Check my classes for today",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "My Timetable"},
            {"action": "click", "element_description": "Timetable"}
        ]
    }
},
{
    "query": "Show my lectures and tutorials",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "My Timetable"},
            {"action": "click", "element_description": "Timetable"}
        ]
    }
},
{
    "query": "Go to my weekly schedule",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "My Timetable"},
            {"action": "click", "element_description": "Timetable"}
        ]
    }
},
{
    "query": "Open my class timetable",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "My Timetable"},
            {"action": "click", "element_description": "Timetable"}
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
},

{
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
{
    "query": "View my results",
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
    "query": "Show my semester results",
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
    "query": "Open my academic transcript",
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
    "query": "To check my current fees",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
                {"action": "click", "element_description": "mySI-net"},
        ]
    }
},
{
    "query": "View my current fees",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "mySI-net"}
        ]
    }
},
{
    "query": "Show outstanding fees",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "mySI-net"}
        ]
    }
},
{
    "query": "Check tuition fees",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "mySI-net"}
        ]
    }
},
{
    "query": "Display my fees balance",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "mySI-net"}
        ]
    }
},
{
    "query": "How much do I owe?",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "mySI-net"}
        ]
    }
},
{
    "query": "My current student fees",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://portal.my.uq.edu.au/#/dashboard"},
            {"action": "click", "element_description": "mySI-net"}
        ]
    }
},
{
    "query": "library loans information",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://www.library.uq.edu.au/"},
            {"action": "click", "element_description": "Log in"},
            {"action": "click", "element_description": "Loans"},
            {"action": "scrape", "element_description": "main content", 
             "processing": "extract loan periods, due dates, renewal policies"}
        ]
    }
},
{
    "query": "Check my library loans",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://www.library.uq.edu.au/"},
            {"action": "click", "element_description": "Log in"},
            {"action": "click", "element_description": "Loans"},
            {"action": "scrape", "element_description": "main content", 
             "processing": "extract loan periods, due dates, renewal policies"}
        ]
    }
},
{
    "query": "View borrowed books and due dates",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://www.library.uq.edu.au/"},
            {"action": "click", "element_description": "Log in"},
            {"action": "click", "element_description": "Loans"},
            {"action": "scrape", "element_description": "main content", 
             "processing": "extract loan periods, due dates, renewal policies"}
        ]
    }
},
{
    "query": "Show my current library checkouts",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://www.library.uq.edu.au/"},
            {"action": "click", "element_description": "Log in"},
            {"action": "click", "element_description": "Loans"},
            {"action": "scrape", "element_description": "main content", 
             "processing": "extract loan periods, due dates, renewal policies"}
        ]
    }
},
{
    "query": "Library books I have on loan",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://www.library.uq.edu.au/"},
            {"action": "click", "element_description": "Log in"},
            {"action": "click", "element_description": "Loans"},
            {"action": "scrape", "element_description": "main content", 
             "processing": "extract loan periods, due dates, renewal policies"}
        ]
    }
},
{
    "query": "Renewal and due dates for my library items",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://www.library.uq.edu.au/"},
            {"action": "click", "element_description": "Log in"},
            {"action": "click", "element_description": "Loans"},
            {"action": "scrape", "element_description": "main content", 
             "processing": "extract loan periods, due dates, renewal policies"}
        ]
    }
},
{
    "query": "View my library account",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://www.library.uq.edu.au/"},
            {"action": "click", "element_description": "Log in"},
            {"action": "click", "element_description": "Loans"},
            {"action": "scrape", "element_description": "main content",
             "processing": "extract loan periods, due dates, renewal policies"}
        ]
    }
},
{
    "query": "Show overdue library books",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://www.library.uq.edu.au/"},
            {"action": "click", "element_description": "Log in"},
            {"action": "click", "element_description": "Loans"},
            {"action": "scrape", "element_description": "main content",
             "processing": "extract loan periods, due dates, renewal policies"}
        ]
    }
},
{
    "query": "What library books do I have out?",
    "plan": {
        "steps": [
            {"action": "goto", "url": "https://www.library.uq.edu.au/"},
            {"action": "click", "element_description": "Log in"},
            {"action": "click", "element_description": "Loans"},
            {"action": "scrape", "element_description": "main content",
             "processing": "extract loan periods, due dates, renewal policies"}
        ]
    }
},
{
        "query": "Open Artificial Intelligence Tutorial 1 pdf",
        "plan": {
            "steps": [
                {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Artificial Intelligence"},
                {"action": "click", "element_description": "Tutorials"}
                {"action": "click", "element_description": "Tutorial 1"}
                {"action": "click", "element_description": "Tutorial 1 - Agent Design"}
                {"action": "click", "element_description": "COMP3702_Tutorial_1.pdf"}
            ]
        }
},
{
        "query": "Open Artificial Intelligence Tutorial 2 pdf",
        "plan": {
            "steps": [
                {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Artificial Intelligence"},
                {"action": "click", "element_description": "Tutorials"}
                {"action": "click", "element_description": "Tutorial 2"}
                {"action": "click", "element_description": "Tutorial 2 - Search (BFS & DFS)"}
                {"action": "click", "element_description": "COMP3702_Tutorial_2.pdf"}
            ]
        }
},
{
        "query": "Open Artificial Intelligence Tutorial 3 pdf",
        "plan": {
            "steps": [
                {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Artificial Intelligence"},
                {"action": "click", "element_description": "Tutorials"}
                {"action": "click", "element_description": "Tutorial 3"}
                {"action": "click", "element_description": "Tutorial 3 - Search (incl. A*)"}
                {"action": "click", "element_description": "COMP3702_Tutorial_3.pdf"}
            ]
        }
},
{
        "query": "Open Artificial Intelligence Tutorial 1 solutions pdf",
        "plan": {
            "steps": [
                {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Artificial Intelligence"},
                {"action": "click", "element_description": "Tutorials"}
                {"action": "click", "element_description": "Tutorial 1"}
                {"action": "click", "element_description": "Tutorial 1 - Solutions"}
                {"action": "click", "element_description": "COMP3702_Tutorial_1_soln.pdf"}
            ]
        }
},
{
        "query": "Open Artificial Intelligence Tutorial 2 solution pdf",
        "plan": {
            "steps": [
                {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Artificial Intelligence"},
                {"action": "click", "element_description": "Tutorials"}
                {"action": "click", "element_description": "Tutorial 2"}
                {"action": "click", "element_description": "Tutorial 2 - Solutions"}
                {"action": "click", "element_description": "COMP3702_Tutorial_2_soln.pdf"}
            ]
        }
},
{
        "query": "Open Artificial Intelligence Tutorial 3 solutions pdf",
        "plan": {
            "steps": [
                {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Artificial Intelligence"},
                {"action": "click", "element_description": "Tutorials"}
                {"action": "click", "element_description": "Tutorial 3"}
                {"action": "click", "element_description": "Tutorial 3 - Solutions"}
                {"action": "click", "element_description": "COMP3702_Tutorial_1_soln.pdf"}
            ]
        }
},
{
        "query": "Open Artificial Intelligence Tutorial 3 solution slides",
        "plan": {
            "steps": [
                {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
                {"action": "click", "element_description": "Artificial Intelligence"},
                {"action": "click", "element_description": "Tutorials"}
                {"action": "click", "element_description": "Tutorial 3"}
                {"action": "click", "element_description": "Tutorial 3 - Solutions"}
                {"action": "click", "element_description": "COMP3702_Tutorial_3_soln_slides.pdf"}
            ]
        }
},
{
    "query": "Open AI Tutorial 1 PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 1"},
            {"action": "click", "element_description": "Tutorial 1 - Agent Design"},
            {"action": "click", "element_description": "COMP3702_Tutorial_1.pdf"}
        ]
    }
},
{
    "query": "Access AI Tutorial 2 PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 2"},
            {"action": "click", "element_description": "Tutorial 2 - Search (BFS & DFS)"},
            {"action": "click", "element_description": "COMP3702_Tutorial_2.pdf"}
        ]
    }
},
{
    "query": "Download AI Tutorial 3 PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 3"},
            {"action": "click", "element_description": "Tutorial 3 - Search (incl. A*)"},
            {"action": "click", "element_description": "COMP3702_Tutorial_3.pdf"}
        ]
    }
},
{
    "query": "Open Tutorial 1 Solutions PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 1"},
            {"action": "click", "element_description": "Tutorial 1 - Solutions"},
            {"action": "click", "element_description": "COMP3702_Tutorial_1_soln.pdf"}
        ]
    }
},
{
    "query": "Open Tutorial 2 Solutions PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 2"},
            {"action": "click", "element_description": "Tutorial 2 - Solutions"},
            {"action": "click", "element_description": "COMP3702_Tutorial_2_soln.pdf"}
        ]
    }
},
{
    "query": "Download Tutorial 3 Solutions PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 3"},
            {"action": "click", "element_description": "Tutorial 3 - Solutions"},
            {"action": "click", "element_description": "COMP3702_Tutorial_3_soln.pdf"}
        ]
    }
},
{
    "query": "Open Tutorial 3 Solution Slides",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 3"},
            {"action": "click", "element_description": "Tutorial 3 - Solutions"},
            {"action": "click", "element_description": "COMP3702_Tutorial_3_soln_slides.pdf"}
        ]
    }
},
{
    "query": "Fetch AI Tutorial 1 PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 1"},
            {"action": "click", "element_description": "Tutorial 1 - Agent Design"},
            {"action": "click", "element_description": "COMP3702_Tutorial_1.pdf"}
        ]
    }
},
{
    "query": "Get AI Tutorial 2 PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 2"},
            {"action": "click", "element_description": "Tutorial 2 - Search (BFS & DFS)"},
            {"action": "click", "element_description": "COMP3702_Tutorial_2.pdf"}
        ]
    }
},
{
    "query": "Open Tutorial 1 Solution PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 1"},
            {"action": "click", "element_description": "Tutorial 1 - Solutions"},
            {"action": "click", "element_description": "COMP3702_Tutorial_1_soln.pdf"}
        ]
    }
},
{
    "query": "Access Tutorial 2 Solution PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 2"},
            {"action": "click", "element_description": "Tutorial 2 - Solutions"},
            {"action": "click", "element_description": "COMP3702_Tutorial_2_soln.pdf"}
        ]
    }
},

{
    "query": "Open slides for Tutorial 3 solutions",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 3"},
            {"action": "click", "element_description": "Tutorial 3 - Solutions"},
            {"action": "click", "element_description": "COMP3702_Tutorial_3_soln_slides.pdf"}
        ]
    }
},
{
    "query": "Retrieve AI Tutorial 1 material",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 1"},
            {"action": "click", "element_description": "Tutorial 1 - Agent Design"},
            {"action": "click", "element_description": "COMP3702_Tutorial_1.pdf"}
        ]
    }
},
{
    "query": "Access Tutorial 2 content PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 2"},
            {"action": "click", "element_description": "Tutorial 2 - Search (BFS & DFS)"},
            {"action": "click", "element_description": "COMP3702_Tutorial_2.pdf"}
        ]
    }
},
{
    "query": "open week 1 AI slides",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Introduction"},
            {"action": "click", "element_description": "Module 0: Introduction"},
            {"action": "click", "element_description": "COMP3702_Module-0_IntroToAI.pdf"},
        ]
    }
},
{
    "query": "open week 1 AI slides",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Search: Week 2 & 3"},
            {"action": "click", "element_description": "Module 1: Search"},
            {"action": "click", "element_description": "COMP3702_Module-1_Search.pdf"},
        ]
    }
},
{
    "query": "Access AI Week 1 lecture slides",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Introduction"},
            {"action": "click", "element_description": "Module 0: Introduction"},
            {"action": "click", "element_description": "COMP3702_Module-0_IntroToAI.pdf"}
        ]
    }
},
{
    "query": "Download AI Week 1 lecture PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Introduction"},
            {"action": "click", "element_description": "Module 0: Introduction"},
            {"action": "click", "element_description": "COMP3702_Module-0_IntroToAI.pdf"}
        ]
    }
},
{
    "query": "Open AI Week 2 lecture slides",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Search: Week 2 & 3"},
            {"action": "click", "element_description": "Module 1: Search"},
            {"action": "click", "element_description": "COMP3702_Module-1_Search.pdf"}
        ]
    }
},
{
    "query": "Fetch AI Week 2 lecture PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Search: Week 2 & 3"},
            {"action": "click", "element_description": "Module 1: Search"},
            {"action": "click", "element_description": "COMP3702_Module-1_Search.pdf"}
        ]
    }
},
{
    "query": "Retrieve AI Week 1 lecture material",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Introduction"},
            {"action": "click", "element_description": "Module 0: Introduction"},
            {"action": "click", "element_description": "COMP3702_Module-0_IntroToAI.pdf"}
        ]
    }
},
{
    "query": "Get AI Week 2 lecture notes PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Search: Week 2 & 3"},
            {"action": "click", "element_description": "Module 1: Search"},
            {"action": "click", "element_description": "COMP3702_Module-1_Search.pdf"}
        ]
    }
},
{
    "query": "Open Week 1 AI slides PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Introduction"},
            {"action": "click", "element_description": "Module 0: Introduction"},
            {"action": "click", "element_description": "COMP3702_Module-0_IntroToAI.pdf"}
        ]
    }
},
{
    "query": "Open Week 2 AI lecture notes",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Search: Week 2 & 3"},
            {"action": "click", "element_description": "Module 1: Search"},
            {"action": "click", "element_description": "COMP3702_Module-1_Search.pdf"}
        ]
    }
},
{
    "query": "Access AI Week 1 lecture slides",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Introduction"},
            {"action": "click", "element_description": "Module 0: Introduction"},
            {"action": "click", "element_description": "COMP3702_Module-0_IntroToAI.pdf"}
        ]
    }
},
{
    "query": "Download AI Week 1 lecture PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Introduction"},
            {"action": "click", "element_description": "Module 0: Introduction"},
            {"action": "click", "element_description": "COMP3702_Module-0_IntroToAI.pdf"}
        ]
    }
},
{
    "query": "Open AI Week 2 lecture slides",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Search: Week 2 & 3"},
            {"action": "click", "element_description": "Module 1: Search"},
            {"action": "click", "element_description": "COMP3702_Module-1_Search.pdf"}
        ]
    }
},
{
    "query": "Fetch AI Week 2 lecture PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Search: Week 2 & 3"},
            {"action": "click", "element_description": "Module 1: Search"},
            {"action": "click", "element_description": "COMP3702_Module-1_Search.pdf"}
        ]
    }
},
{
    "query": "Retrieve AI Week 1 lecture material",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Introduction"},
            {"action": "click", "element_description": "Module 0: Introduction"},
            {"action": "click", "element_description": "COMP3702_Module-0_IntroToAI.pdf"}
        ]
    }
},
{
    "query": "Get AI Week 2 lecture notes PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Search: Week 2 & 3"},
            {"action": "click", "element_description": "Module 1: Search"},
            {"action": "click", "element_description": "COMP3702_Module-1_Search.pdf"}
        ]
    }
},
{
    "query": "Open Week 1 AI slides PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Introduction"},
            {"action": "click", "element_description": "Module 0: Introduction"},
            {"action": "click", "element_description": "COMP3702_Module-0_IntroToAI.pdf"}
        ]
    }
},
{
    "query": "Open Week 2 AI lecture notes",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Search: Week 2 & 3"},
            {"action": "click", "element_description": "Module 1: Search"},
            {"action": "click", "element_description": "COMP3702_Module-1_Search.pdf"}
        ]
    }
},
{
    "query": "Open Artificial Intelligence Week 1 lecture slides",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Introduction"},
            {"action": "click", "element_description": "Module 0: Introduction"},
            {"action": "click", "element_description": "COMP3702_Module-0_IntroToAI.pdf"}
        ]
    }
},
{
    "query": "Download Artificial Intelligence Week 1 PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Introduction"},
            {"action": "click", "element_description": "Module 0: Introduction"},
            {"action": "click", "element_description": "COMP3702_Module-0_IntroToAI.pdf"}
        ]
    }
},
{
    "query": "Access Artificial Intelligence Week 2 lecture slides",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Search: Week 2 & 3"},
            {"action": "click", "element_description": "Module 1: Search"},
            {"action": "click", "element_description": "COMP3702_Module-1_Search.pdf"}
        ]
    }
},
{
    "query": "Fetch Artificial Intelligence Week 2 PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Search: Week 2 & 3"},
            {"action": "click", "element_description": "Module 1: Search"},
            {"action": "click", "element_description": "COMP3702_Module-1_Search.pdf"}
        ]
    }
},
{
    "query": "Retrieve Artificial Intelligence Week 1 lecture material",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Introduction"},
            {"action": "click", "element_description": "Module 0: Introduction"},
            {"action": "click", "element_description": "COMP3702_Module-0_IntroToAI.pdf"}
        ]
    }
},
{
    "query": "Open Artificial Intelligence Week 3 lecture slides",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Search: Week 2 & 3"},
            {"action": "click", "element_description": "Module 2: Advanced Search"},
            {"action": "click", "element_description": "COMP3702_Module-2_AdvancedSearch.pdf"}
        ]
    }
},
{
    "query": "Download Artificial Intelligence Week 3 PDF notes",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Search: Week 2 & 3"},
            {"action": "click", "element_description": "Module 2: Advanced Search"},
            {"action": "click", "element_description": "COMP3702_Module-2_AdvancedSearch.pdf"}
        ]
    }
},
{
    "query": "Access Artificial Intelligence Week 1 tutorial PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 1"},
            {"action": "click", "element_description": "Tutorial 1 - Agent Design"},
            {"action": "click", "element_description": "COMP3702_Tutorial_1.pdf"}
        ]
    }
},
{
    "query": "Open Artificial Intelligence Week 2 tutorial PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Tutorials"},
            {"action": "click", "element_description": "Tutorial 2"},
            {"action": "click", "element_description": "Tutorial 2 - Search (BFS & DFS)"},
            {"action": "click", "element_description": "COMP3702_Tutorial_2.pdf"}
        ]
    }
},
{
    "query": "Open Artificial Intelligence Assignment 0",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Assessment"},
            {"action": "click", "element_description": "Assignment 0 - 2025"},
            {"action": "click", "element_description": "Assignment 0 - Task Description"},
            {"action": "click", "element_description": "COMP3702_2025_Assignment-0.pdf"}
        ]
    }
},
{
    "query": "Open Artificial Intelligence Assessignment 1",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Assessment"},
            {"action": "click", "element_description": "Assignment 1 - 2025"},
            {"action": "click", "element_description": "Assignment 1 - Task Description"},
            {"action": "click", "element_description": "COMP3702_2025_Assignment-1.pdf"}
        ]
    }
},

{
    "query": "To Submit Artificial Intelligence Assignment 0 Code",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Assessment"},
            {"action": "click", "element_description": "Assignment 0 - 2025"},
            {"action": "click", "element_description": "Assignment 0 - Code"},
            {"action": "click", "element_description": "Launch"}
        ]
    }
},
{
    "query": "To submit Artificial Intelligence Assessignment 0 Report",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Assessment"},
            {"action": "click", "element_description": "Assignment 0 - 2025"},
            {"action": "click", "element_description": "Assignment 0 - Report"},
            {"action": "click", "element_description": "Launch"}
        ]
    }
},
{
    "query": "Open AI Assignment 0 PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Assessment"},
            {"action": "click", "element_description": "Assignment 0 - 2025"},
            {"action": "click", "element_description": "Assignment 0 - Task Description"},
            {"action": "click", "element_description": "COMP3702_2025_Assignment-0.pdf"}
        ]
    }
},
{
    "query": "Access Artificial Intelligence Assignment 1 PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Assessment"},
            {"action": "click", "element_description": "Assignment 1 - 2025"},
            {"action": "click", "element_description": "Assignment 1 - Task Description"},
            {"action": "click", "element_description": "COMP3702_2025_Assignment-1.pdf"}
        ]
    }
},
{
    "query": "Submit code for AI Assignment 0",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Assessment"},
            {"action": "click", "element_description": "Assignment 0 - 2025"},
            {"action": "click", "element_description": "Assignment 0 - Code"},
            {"action": "click", "element_description": "Launch"}
        ]
    }
},
{
    "query": "Submit AI Assignment 0 report",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Assessment"},
            {"action": "click", "element_description": "Assignment 0 - 2025"},
            {"action": "click", "element_description": "Assignment 0 - Report"},
            {"action": "click", "element_description": "Launch"}
        ]
    }
},
{
    "query": "Launch Assignment 1 task PDF for Artificial Intelligence",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Assessment"},
            {"action": "click", "element_description": "Assignment 1 - 2025"},
            {"action": "click", "element_description": "Assignment 1 - Task Description"},
            {"action": "click", "element_description": "COMP3702_2025_Assignment-1.pdf"}
        ]
    }
},
{
    "query": "Upload code for Artificial Intelligence Assignment 0",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Assessment"},
            {"action": "click", "element_description": "Assignment 0 - 2025"},
            {"action": "click", "element_description": "Assignment 0 - Code"},
            {"action": "click", "element_description": "Launch"}
        ]
    }
},
{
    "query": "Upload report for AI Assignment 0",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Assessment"},
            {"action": "click", "element_description": "Assignment 0 - 2025"},
            {"action": "click", "element_description": "Assignment 0 - Report"},
            {"action": "click", "element_description": "Launch"}
        ]
    }
},
{
    "query": "Open AI Assignment 0 task description PDF",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://learn.uq.edu.au/ultra/course"},
            {"action": "click", "element_description": "Artificial Intelligence"},
            {"action": "click", "element_description": "Assessment"},
            {"action": "click", "element_description": "Assignment 0 - 2025"},
            {"action": "click", "element_description": "Assignment 0 - Task Description"},
            {"action": "click", "element_description": "COMP3702_2025_Assignment-0.pdf"}
        ]
    }
},
{
    "query": "To book Group meeting rooms",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://uqbookit.uq.edu.au/app/booking-types"},
            {"action": "click", "element_description": "Library rooms"},
            {"action": "click", "element_description": "Group meeting rooms"},
            {"action": "click", "element_description": "12N204A Central Library"},
            {"action": "click", "element_description": "Show availability"},
        ]
    },
},
{
    "query": "To book One-person meeting booth",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://uqbookit.uq.edu.au/app/booking-types"},
            {"action": "click", "element_description": "Library rooms"},
            {"action": "click", "element_description": "One-person meeting booth"},
            {"action": "click", "element_description": "12N204-01 Central Library"},
            {"action": "click", "element_description": "Show availability"},
        ]
    }

},
{
    "query": "To book Two-person meeting booth",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://uqbookit.uq.edu.au/app/booking-types"},
            {"action": "click", "element_description": "Library rooms"},
            {"action": "click", "element_description": "Two-person meeting booth"},
            {"action": "click", "element_description": "12-N121-01 Central Library"},
            {"action": "click", "element_description": "Show availability"},
        ]
    }

},
{
    "query": "Reserve a group study room",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://uqbookit.uq.edu.au/app/booking-types"},
            {"action": "click", "element_description": "Library rooms"},
            {"action": "click", "element_description": "Group meeting rooms"},
            {"action": "click", "element_description": "12N204A Central Library"},
            {"action": "click", "element_description": "Show availability"}
        ]
    }
},
{
    "query": "Book a one-person booth in library",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://uqbookit.uq.edu.au/app/booking-types"},
            {"action": "click", "element_description": "Library rooms"},
            {"action": "click", "element_description": "One-person meeting booth"},
            {"action": "click", "element_description": "12N204-01 Central Library"},
            {"action": "click", "element_description": "Show availability"}
        ]
    }
},
{
    "query": "Reserve a two-person study booth",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://uqbookit.uq.edu.au/app/booking-types"},
            {"action": "click", "element_description": "Library rooms"},
            {"action": "click", "element_description": "Two-person meeting booth"},
            {"action": "click", "element_description": "12-N121-01 Central Library"},
            {"action": "click", "element_description": "Show availability"}
        ]
    }
},
{
    "query": "Check availability of group meeting rooms",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://uqbookit.uq.edu.au/app/booking-types"},
            {"action": "click", "element_description": "Library rooms"},
            {"action": "click", "element_description": "Group meeting rooms"},
            {"action": "click", "element_description": "12N204A Central Library"},
            {"action": "click", "element_description": "Show availability"}
        ]
    }
},
{
    "query": "Reserve a private single-person booth",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://uqbookit.uq.edu.au/app/booking-types"},
            {"action": "click", "element_description": "Library rooms"},
            {"action": "click", "element_description": "One-person meeting booth"},
            {"action": "click", "element_description": "12N204-01 Central Library"},
            {"action": "click", "element_description": "Show availability"}
        ]
    }
},
{
    "query": "Book a study booth for two people",
    "plan": {
        "steps": [
            {"action": "goto", "element_description": "https://uqbookit.uq.edu.au/app/booking-types"},
            {"action": "click", "element_description": "Library rooms"},
            {"action": "click", "element_description": "Two-person meeting booth"},
            {"action": "click", "element_description": "12-N121-01 Central Library"},
            {"action": "click", "element_description": "Show availability"}
        ]
    }
}

]
