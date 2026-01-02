from config.supabase_config import supabase
from datetime import datetime

class DBService:
    @staticmethod
    def create_report(user_id, file_url, raw_data, metadata=None):
        data = {
            "user_id": user_id,
            "file_url": file_url,
            "raw_data": raw_data,
            "metadata": metadata or {},
            "status": "pending_confirmation",
            "created_at": datetime.utcnow().isoformat()
        }

        response = supabase.table("reports").insert(data).execute()

        
        if not response.data or len(response.data) == 0:
            raise Exception(
                f"Report insert failed. Supabase response: {response}"
            )

        return response.data[0]


    @staticmethod
    def update_report_status(report_id, status, confirmed_data=None, analysis_result=None):
        """
        Updates the report status (e.g., to 'analyzed') and saves results.
        """
        update_payload = {"status": status}
        
        if confirmed_data:
            update_payload["confirmed_data"] = confirmed_data
        
        if analysis_result:
            update_payload["analysis_data"] = analysis_result

        response = supabase.table("reports")\
            .update(update_payload)\
            .eq("id", report_id)\
            .execute()
        return response.data

    @staticmethod
    def get_user_history(user_id):
        """Fetches past reports for the History page[cite: 71]."""
        response = supabase.table("reports")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        return response.data

    @staticmethod
    def get_report_by_id(report_id):
        """Fetches a single report details."""
        response = supabase.table("reports")\
            .select("*")\
            .eq("id", report_id)\
            .execute()
        return response.data[0] if response.data else None
