from src.config import Config
from src.models.department import Department
from src.models.dept_keyword import DeptKeyword
from src.models.user_question import DeptType

def populate_departments_and_keywords():
    """
    Populate departments with descriptions and their associated keywords
    """
    session = Config.get_session()
    
    # Department descriptions
    department_descriptions = {
        DeptType.HR: "Human Resources handles employee relations, benefits, payroll, hiring, training, and workplace policies.",
        DeptType.IT: "Information Technology manages computers, software, networks, email, technical support, and cybersecurity.",
        DeptType.Security: "Security manages building access, visitor management, surveillance, incident response, and workplace safety."
    }
    
    # Department keywords
    department_keywords = {
        DeptType.HR: [
            "salary", "payroll", "leave", "vacation", "sick leave", "maternity", "paternity",
            "benefits", "insurance", "health", "dental", "401k", "retirement", "pension",
            "hiring", "recruitment", "onboarding", "offboarding", "termination", "resignation",
            "performance", "review", "appraisal", "promotion", "training", "development",
            "harassment", "discrimination", "complaint", "grievance", "policy", "handbook",
            "employee", "staff", "colleague", "manager", "supervisor", "team lead",
            "contract", "employment", "probation", "full-time", "part-time", "contractor",
            "overtime", "shift", "schedule", "attendance", "time off", "pto", "holiday"
        ],
        
        DeptType.IT: [
            "computer", "laptop", "desktop", "monitor", "keyboard", "mouse", "printer",
            "software", "application", "app", "program", "install", "update", "upgrade",
            "password", "login", "access", "account", "credentials", "authentication",
            "network", "wifi", "internet", "connection", "server", "database", "cloud",
            "email", "outlook", "gmail", "attachment", "spam", "phishing",
            "backup", "restore", "file", "folder", "document", "excel", "word", "pdf",
            "virus", "malware", "antivirus", "security", "firewall", "vpn", "remote",
            "troubleshoot", "bug", "error", "crash", "freeze", "slow", "performance",
            "hard drive", "storage", "memory", "ram", "cpu", "hardware", "device"
        ],
        
        DeptType.Security: [
            "badge", "access card", "keycard", "entry", "door", "gate", "building",
            "visitor", "guest", "contractor", "vendor", "escort", "registration",
            "camera", "surveillance", "monitoring", "cctv", "recording", "footage",
            "incident", "breach", "unauthorized", "suspicious", "threat", "emergency",
            "evacuation", "fire drill", "safety", "protocol", "procedure", "compliance",
            "parking", "vehicle", "license plate", "traffic", "patrol", "guard",
            "alarm", "alert", "notification", "report", "investigation", "evidence",
            "tailgating", "piggybacking", "social engineering", "phishing", "scam",
            "theft", "vandalism", "trespassing", "assault", "harassment", "violence"
        ]
    }
    
    try:
        print("🔧 Starting department and keyword population...")
        
        # Step 1: Create/Update Departments
        print("\n📋 Processing departments...")
        departments = {}
        
        for dept_type, description in department_descriptions.items():
            existing_dept = Department.get_by_name(session, dept_type)
            
            if existing_dept:
                # Update description if it exists
                existing_dept.description = description
                departments[dept_type] = existing_dept
                print(f"✅ Updated {dept_type.value} department")
            else:
                # Create new department
                new_dept = Department.create(session, dept_type, description)
                departments[dept_type] = new_dept
                print(f"✅ Created {dept_type.value} department")
        
        # Commit department changes
        session.commit()
        print("✅ All departments saved successfully!")
        
        # Step 2: Add Keywords
        print("\n🔑 Processing keywords...")
        total_keywords_added = 0
        
        for dept_type, keywords in department_keywords.items():
            dept = departments[dept_type]
            
            # Clear existing keywords for this department (optional - remove if you want to keep existing)
            existing_keywords = DeptKeyword.get_by_dept_id(session, dept.id)
            if existing_keywords:
                for existing in existing_keywords:
                    session.delete(existing)
                print(f"🗑️  Cleared {len(existing_keywords)} existing keywords for {dept_type.value}")
            
            # Add new keywords
            keywords_added = 0
            for keyword in keywords:
                try:
                    DeptKeyword.create(session, dept.id, keyword)
                    keywords_added += 1
                except Exception as e:
                    print(f"⚠️  Warning: Could not add keyword '{keyword}' for {dept_type.value}: {e}")
                    session.rollback()
                    continue
            
            total_keywords_added += keywords_added
            print(f"✅ Added {keywords_added} keywords for {dept_type.value}")
        
        # Final commit
        session.commit()
        print(f"✅ All {total_keywords_added} keywords saved successfully!")
        
        # Step 3: Display Summary
        print("\n📊 SUMMARY:")
        print("=" * 50)
        
        for dept_type in department_descriptions.keys():
            dept = Department.get_by_name(session, dept_type)
            keyword_count = len(DeptKeyword.get_by_dept_id(session, dept.id))
            
            print(f"🏢 {dept_type.value}:")
            print(f"   📝 Description: {dept.description[:60]}...")
            print(f"   🔑 Keywords: {keyword_count}")
            print()
        
        total_depts = len(department_descriptions)
        total_keywords = sum(len(keywords) for keywords in department_keywords.values())
        
        print(f"🎉 SUCCESS! Populated {total_depts} departments with {total_keywords} total keywords!")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error populating departments and keywords: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        session.close()

def verify_data():
    """
    Verify that departments and keywords were populated correctly
    """
    session = Config.get_session()
    
    try:
        print("\n🔍 VERIFICATION:")
        print("=" * 50)
        
        # Check departments
        departments = Department.get_all(session)
        print(f"📋 Total Departments: {len(departments)}")
        
        for dept in departments:
            keywords = DeptKeyword.get_by_dept_id(session, dept.id)
            print(f"   • {dept.name.value}: {len(keywords)} keywords")
        
        # Check total keywords
        total_keywords = DeptKeyword.get_count(session)
        print(f"🔑 Total Keywords: {total_keywords}")
        
        # Sample some keywords
        print("\n📝 Sample Keywords:")
        for dept in departments:
            keywords = DeptKeyword.get_by_dept_id(session, dept.id)
            sample_keywords = [k.keyword for k in keywords[:5]]
            print(f"   {dept.name.value}: {', '.join(sample_keywords)}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
        
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Department and Keyword Population Script")
    print("=" * 50)
    
    # Run population
    success = populate_departments_and_keywords()
    
    if success:
        # Run verification
        verify_data()
        print("\n✨ Script completed successfully!")
    else:
        print("\n💥 Script failed. Check the error messages above.")