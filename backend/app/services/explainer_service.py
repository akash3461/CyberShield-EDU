# import logging
# 
# logger = logging.getLogger("CyberShield")
# 
# class ScamExplainerService:
#     """
#     Pillar 1: LLM-Driven Scam Explainer (Cyber-Tutor).
#     Provides a narrative breakdown of WHY a scan was flagged, targeting student education.
#     """
# 
#     def generate_explanation(self, scan_type: str, result: dict) -> str:
#         """
#         Generates a contextualized explanation based on scan forensics.
#         In a production environment, this would call an LLM (Gemma/Mistral).
#         For this stabilization phase, we use a logic-driven template engine.
#         """
#         prediction = result.get("prediction", "safe")
#         confidence = result.get("confidence", 0)
#         
#         if prediction == "safe" and confidence > 0.8:
#             return "This content appears highly legitimate. It lacks common psychological pressure tactics and technical anomalies (like homoglyphs or suspicious server origins). Continue as usual!"
# 
#         # Core logic for scams
#         explanation_blocks = []
#         
#         if scan_type == "url":
#             forensics = result.get("forensics", {})
#             metadata = result.get("metadata", {})
#             
#             explanation_blocks.append(f"CyberShield detected a {prediction} indicator on this link with {confidence*100:.1f}% AI confidence.")
#             
#             if metadata.get("entropy", 0) > 3.5:
#                 explanation_blocks.append("- The domain looks 'machine-generated' (high entropy). Real companies use readable, branded names.")
#             
#             asn = forensics.get("asn_info", {}).get("isp", "Unknown")
#             if "Private" in asn or "Cloudflare" in asn:
#                 explanation_blocks.append(f"- This link is hosted on {asn}. While not always malicious, many scam sites hide behind generic hosting to avoid detection.")
# 
#             if any("Homoglyph" in r for r in result.get("reasoning", [])):
#                 explanation_blocks.append("- **CRITICAL**: We detected 'typosquatting' (visual trickery where characters look like letters from real brands but are actually different symbols).")
# 
#         elif scan_type == "text":
#             insights = result.get("insights", {})
#             explanation_blocks.append("Our Linguistic Analysis Engine flagged several markers typically used in social engineering:")
#             
#             if "congratulations" in str(result.get("highlights", [])).lower():
#                 explanation_blocks.append("- **The Lure**: It starts with 'Congratulations'. Scammers use positive emotional triggers to make you lower your guard.")
#             
#             if "fee" in str(result.get("highlights", [])).lower():
#                 explanation_blocks.append("- **The Financial Hook**: It mentions a 'fee' or 'payment'. Legitimate internships or scholarships almost NEVER ask for upfront money.")
#             
#             if insights.get("complexity") == "Low (Likely Automated)":
#                 explanation_blocks.append("- **Automated Pattern**: The phrasing is repetitive and simple, a hallmark of mass-scale bot campaigns.")
# 
#         elif scan_type == "pdf":
#             forensics = result.get("metadata", {}).get("forensics", {})
#             ai_res = result.get("ai_analysis", {})
#             url_res = result.get("url_analysis", [])
#             
#             explanation_blocks.append("### 📄 Forensic Intelligence Briefing\n")
#             
#             # AI Linguistic Hook
#             if ai_res and ai_res.get("prediction") == "scam":
#                 explanation_blocks.append(f"- **Linguistic Intent**: Our AI detected high-risk language patterns. The document uses 'Psychological Triggers' (like {', '.join(ai_res.get('reasoning', ['urgent demands'])[:2])}) that are common in fraudulent internship and refund scams.")
#             
#             # Structural/Original check
#             author = forensics.get("author", "Unknown")
#             creator = forensics.get("creator_tool", "Unknown")
#             if "Python" in creator or "Unknown" in creator or "Admin" in author:
#                 explanation_blocks.append(f"- **Structural Integrity**: The document metadata is suspicious. It was created by '{author}' using '{creator}'. Genuine corporate or university documents are typically signed by a verified authoring suite (like Adobe Acrobat or Microsoft Word).")
#             
#             # Network Vector (Pillar 8 integration)
#             if url_res:
#                 scam_urls = [u for u in url_res if u.get("prediction") == "scam"]
#                 if scam_urls:
#                     explanation_blocks.append(f"- **Network Exposure**: We found {len(scam_urls)} high-risk 'Ghost-Links' hidden inside the document layers. These lead to server origins with poor reputation or unknown network owners.")
#                 else:
#                     explanation_blocks.append(f"- **Link Audit**: We extracted {len(url_res)} internal links. While not blocked, their global origins were scanned for safety.")
# 
#             if not forensics.get("is_digitally_signed"):
#                 explanation_blocks.append("- **Trust Marker Missing**: This file is missing a 'Digital Signature'. An official offer letter or invoice should be digitally signed by the issuing organization to prevent tampering.")
# 
#         if not explanation_blocks:
#             return "This scan was flagged due to a combination of suspicious heuristic patterns and AI prediction scores. Please refer to the Technical Forensics panel for raw data."
# 
#         return " ".join(explanation_blocks)
# 
# scam_explainer = ScamExplainerService()
