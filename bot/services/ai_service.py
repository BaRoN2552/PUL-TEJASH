import httpx
import logging
from datetime import date, timedelta
from bot.config import settings
from bot.services.report_service import report_service

logger = logging.getLogger(__name__)

class AIService:
    async def get_financial_advice(self, user_id: int) -> str:
        """
        Analyzes the user's spending patterns and returns 5 tailored financial tips.
        Connects to OpenAI GPT-4 if OPENAI_API_KEY is present, otherwise falls back
        to a highly analytical rule-based engine in Uzbek.
        """
        # Fetch current month stats
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        stats = await report_service.get_summary_stats(user_id, start_of_month, today)
        
        incomes = stats["incomes"]
        expenses = stats["expenses"]
        savings = stats["savings"]
        savings_pct = stats["savings_pct"]
        categories = stats["categories"]
        
        # 1. Check if OpenAI API key is set and call GPT-4
        if settings.openai_api_key:
            try:
                system_prompt = (
                    "Siz shaxsiy moliyaviy maslahatchisiz. Foydalanuvchining oylik moliyaviy ma'lumotlarini tahlil qilib, "
                    "unga 5 ta juda aniq, amaliy va foydali o'zbek tilidagi moliyaviy maslahatlarni bering. Maslahatlar qisqa, "
                    "samimiy va raqamlarga asoslangan bo'lsin. Format: 1. Maslahat, 2. Maslahat, etc."
                )
                user_data_summary = (
                    f"Jami Kirim: {incomes:,.0f} UZS\n"
                    f"Jami Chiqim: {expenses:,.0f} UZS\n"
                    f"Tejalgan Summa: {savings:,.0f} UZS ({savings_pct:.1f}%)\n"
                    f"Kategoriyalar bo'yicha chiqimlar: {categories}\n"
                )
                
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                        json={
                            "model": "gpt-4-turbo",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_data_summary}
                            ],
                            "temperature": 0.7
                        }
                    )
                    if response.status_code == 200:
                        content = response.json()["choices"][0]["message"]["content"]
                        return content
                    else:
                        logger.error(f"OpenAI API error: {response.text}")
            except Exception as e:
                logger.error(f"Error calling OpenAI API: {e}")

        # 2. Rule-based Fallback System in Uzbek
        logger.info("Using Rule-based Advisor Fallback...")
        
        tips = []
        
        # Sort categories to find top expense
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        top_cat = sorted_categories[0][0] if sorted_categories else None
        top_cat_amount = sorted_categories[0][1] if sorted_categories else 0
        
        # Tip 1: Savings rate analysis
        if incomes == 0:
            tips.append("💰 Hozircha bu oy uchun daromadlar kiritilmadi. Daromad va oylik maoshingizni yozib borishni unutmang.")
        elif savings_pct < 10:
            tips.append(f"💎 Bu oy daromadingizning atigi {savings_pct:.0f}% qismini tejamabsiz. Ideal holatda daromadning kamida 20% qismini jamg'arish tavsiya etiladi. Hozirgi tejash darajangiz past.")
        elif savings_pct >= 20:
            tips.append(f"🎉 Ajoyib natija! Bu oy daromadingizning {savings_pct:.0f}% qismini tejab qoldingiz. Moliyaviy intizomingiz yuqori darajada.")
        else:
            tips.append(f"📈 Siz bu oy daromadingizning {savings_pct:.0f}% qismini tejab qoldingiz. Yaxshi ko'rsatkich, lekin buni 20% ga yetkazishga harakat qilib ko'ring.")

        # Tip 2: Top Expense Analysis
        if top_cat and top_cat_amount > 0:
            potential_saving = top_cat_amount * 0.1
            tips.append(f"🍕 Eng katta xarajatingiz: **{top_cat}** ({top_cat_amount:,.0f} so'm). Agar ushbu kategoriyadagi xarajatlarni atigi 10% ga qisqartirsangiz, yana {potential_saving:,.0f} so'm tejashingiz mumkin.")

        # Tip 3: Cafe/Entertainment specific check
        cafe_amount = 0
        for cat_name, amt in categories.items():
            if "kafe" in cat_name.lower() or "restoran" in cat_name.lower() or "oziq-ovqat" in cat_name.lower():
                cafe_amount += amt
        if cafe_amount > 0 and incomes > 0:
            cafe_pct = (cafe_amount / incomes) * 100
            if cafe_pct > 15:
                tips.append(f"☕ Oziq-ovqat va Kafe xarajatlaringiz umumiy daromadingizning {cafe_pct:.0f}% ini tashkil etdi. Uyda ovqatlanish yoki qahvani uyda tayyorlash orqali moliyaviy yukni sezilarli kamaytira olasiz.")

        # Tip 4: Emergency Fund advice
        tips.append("🛡️ **Favqulodda vaziyatlar fondi (Xavfsizlik yostiqchasi):** Kamida 3 oylik xarajatingizga teng mablag'ni alohida hisobda jamg'arib boring. Bu kutilmagan vaziyatlarda qarz olishdan asraydi.")

        # Tip 5: General advice
        tips.append("📝 **50/30/20 qoidasiga amal qiling:** Daromadlaringizning 50% qismini majburiy ehtiyojlarga (ijara, kommunal, ovqat), 30% ini xohishlarga (ko'ngilochar, kiyim) va 20% ini jamg'armalarga ajrating.")

        # Build output string
        output = "🤖 **AI MOLIYAVIY MASLAHATLARI:**\n\n"
        for i, tip in enumerate(tips[:5], 1):
            output += f"{i}. {tip}\n\n"
            
        return output

ai_service = AIService()
