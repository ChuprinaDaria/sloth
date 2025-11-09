"""
Photo Analysis Service - Deep image analysis using Google Vision API and OpenAI
"""
import os
import base64
import json
from google.cloud import vision
from openai import OpenAI
from django.utils import timezone
from .models import Photo
from apps.embeddings.models import Embedding


class PhotoAnalysisService:
    """
    Детальний аналіз фото з використанням Google Vision API та OpenAI
    """

    def __init__(self, tenant_schema):
        self.tenant_schema = tenant_schema
        self.vision_client = vision.ImageAnnotatorClient()
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def analyze_photo(self, photo_id, file_path):
        """
        Повний аналіз фото з детальними результатами

        Args:
            photo_id: ID фото в БД
            file_path: шлях до файлу (локальний або S3 URL)

        Returns:
            dict: результати аналізу
        """
        try:
            photo = Photo.objects.get(id=photo_id)
            photo.processing_status = 'processing'
            photo.save()

            # Read image
            image_content = self._read_image(file_path)
            image = vision.Image(content=image_content)

            # Run all Google Vision analyses in parallel
            results = {}

            # 1. Label Detection (що на фото)
            labels_response = self.vision_client.label_detection(image=image)
            results['labels'] = [
                {
                    'description': label.description,
                    'score': label.score,
                    'confidence': label.score
                }
                for label in labels_response.label_annotations
            ]

            # 2. Object Detection (конкретні об'єкти з локацією)
            objects_response = self.vision_client.object_localization(image=image)
            results['detected_objects'] = [
                {
                    'name': obj.name,
                    'score': obj.score,
                    'bounding_box': {
                        'vertices': [
                            {'x': vertex.x, 'y': vertex.y}
                            for vertex in obj.bounding_poly.normalized_vertices
                        ]
                    }
                }
                for obj in objects_response.localized_object_annotations
            ]

            # 3. Image Properties (кольори)
            properties_response = self.vision_client.image_properties(image=image)
            results['colors'] = [
                {
                    'color': {
                        'red': color.color.red,
                        'green': color.color.green,
                        'blue': color.color.blue
                    },
                    'score': color.score,
                    'pixel_fraction': color.pixel_fraction
                }
                for color in properties_response.image_properties_annotation.dominant_colors.colors[:10]
            ]

            # 4. Face Detection (обличчя, емоції)
            faces_response = self.vision_client.face_detection(image=image)
            results['faces'] = [
                {
                    'joy': self._likelihood_name(face.joy_likelihood),
                    'sorrow': self._likelihood_name(face.sorrow_likelihood),
                    'anger': self._likelihood_name(face.anger_likelihood),
                    'surprise': self._likelihood_name(face.surprise_likelihood),
                    'confidence': face.detection_confidence,
                    'bounding_box': {
                        'vertices': [
                            {'x': vertex.x, 'y': vertex.y}
                            for vertex in face.bounding_poly.vertices
                        ]
                    }
                }
                for face in faces_response.face_annotations
            ]

            # 5. Text Detection (OCR)
            text_response = self.vision_client.text_detection(image=image)
            results['text'] = text_response.text_annotations[0].description if text_response.text_annotations else ''

            # 6. Enhanced AI Analysis для beauty/hair
            detailed_analysis = self._deep_ai_analysis(image_content, results)

            # Save results
            photo.labels = results['labels']
            photo.detected_objects = results['detected_objects']
            photo.colors = results['colors']
            photo.faces = results['faces']
            photo.text = results['text']
            photo.detailed_analysis = detailed_analysis
            photo.is_processed = True
            photo.processing_status = 'completed'
            photo.processed_at = timezone.now()
            photo.save()

            # Create vector embedding
            self._create_embedding(photo, detailed_analysis)

            return {
                'status': 'success',
                'photo_id': photo_id,
                'results': results,
                'detailed_analysis': detailed_analysis
            }

        except Exception as e:
            photo.processing_status = 'failed'
            photo.processing_error = str(e)
            photo.save()
            return {
                'status': 'error',
                'error': str(e)
            }

    def _deep_ai_analysis(self, image_content, vision_results):
        """
        Детальний AI аналіз для beauty індустрії (волосся, шкіра, макіяж)
        """
        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_content).decode('utf-8')

            # Prepare context from Vision API results
            labels = ', '.join([l['description'] for l in vision_results['labels'][:10]])
            objects = ', '.join([o['name'] for o in vision_results['detected_objects'][:10]])
            dominant_colors = self._format_colors(vision_results['colors'][:5])

            prompt = f"""
Analyze this image in extreme detail for beauty/salon services. Provide a comprehensive analysis.

Context from image analysis:
- Detected labels: {labels}
- Detected objects: {objects}
- Dominant colors: {dominant_colors}

Provide detailed analysis in JSON format:

{{
  "category": "hair|skin|nails|makeup|other",
  "hair_analysis": {{
    "present": true/false,
    "color": "natural color description",
    "is_natural": true/false,
    "condition": "healthy|damaged|dry|oily|normal",
    "length": "short|medium|long|very_long (in cm if visible)",
    "texture": "straight|wavy|curly|coily",
    "style": "description of hairstyle",
    "highlights": "description if present",
    "visible_treatments": ["coloring", "balayage", "highlights", etc],
    "recommendations": ["suggested services"]
  }},
  "skin_analysis": {{
    "present": true/false,
    "tone": "fair|light|medium|olive|tan|dark",
    "condition": "clear|oily|dry|combination|acne_prone",
    "visible_concerns": ["wrinkles", "acne", "dark_spots", etc],
    "recommendations": ["suggested treatments"]
  }},
  "nails_analysis": {{
    "present": true/false,
    "condition": "well_maintained|needs_care",
    "length": "short|medium|long",
    "style": "natural|manicured|polish|extensions",
    "recommendations": ["suggested services"]
  }},
  "makeup_analysis": {{
    "present": true/false,
    "style": "natural|dramatic|evening|bridal",
    "visible_products": ["lipstick", "eyeshadow", etc],
    "recommendations": ["suggested services"]
  }},
  "overall_assessment": "detailed description of what is shown in the image",
  "service_suggestions": ["list of specific services that would be relevant"],
  "key_features": ["most important features to mention"],
  "comparison_keywords": ["keywords for finding similar images in database"]
}}

Be extremely detailed and specific. For hair: mention exact color nuances, condition indicators, length measurements if visible, styling details. For skin: note tone, texture, any visible concerns. Always provide actionable recommendations.
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4 with vision
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            analysis = json.loads(response.choices[0].message.content)
            return analysis

        except Exception as e:
            print(f"Error in deep AI analysis: {e}")
            return {
                'error': str(e),
                'category': 'unknown',
                'overall_assessment': 'Analysis failed'
            }

    def _create_embedding(self, photo, detailed_analysis):
        """
        Створює векторний ембеддінг для фото на основі аналізу
        """
        try:
            # Create text representation of the image for embedding
            text_parts = []

            # Add user description if provided
            if photo.description:
                text_parts.append(f"User description: {photo.description}")

            # Add overall assessment
            if 'overall_assessment' in detailed_analysis:
                text_parts.append(f"Visual analysis: {detailed_analysis['overall_assessment']}")

            # Add hair analysis details
            if detailed_analysis.get('hair_analysis', {}).get('present'):
                hair = detailed_analysis['hair_analysis']
                hair_desc = f"Hair: {hair.get('color', '')} {hair.get('length', '')} {hair.get('texture', '')} {hair.get('style', '')}"
                text_parts.append(hair_desc)

            # Add service suggestions
            if 'service_suggestions' in detailed_analysis:
                text_parts.append(f"Relevant services: {', '.join(detailed_analysis['service_suggestions'])}")

            # Add comparison keywords
            if 'comparison_keywords' in detailed_analysis:
                text_parts.append(f"Keywords: {', '.join(detailed_analysis['comparison_keywords'])}")

            # Combine all parts
            embedding_text = " | ".join(text_parts)

            if not embedding_text:
                return

            # Create embedding using OpenAI
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=embedding_text
            )

            # Note: Actually storing the vector requires raw SQL with pgvector
            # For now, we store the text representation
            Embedding.objects.create(
                source_type='photo',
                source_id=photo.id,
                content=embedding_text,
                metadata={
                    'analysis_summary': detailed_analysis.get('overall_assessment', ''),
                    'category': detailed_analysis.get('category', 'unknown'),
                    'service_suggestions': detailed_analysis.get('service_suggestions', [])
                }
            )

        except Exception as e:
            print(f"Error creating embedding: {e}")

    def find_similar_photos(self, client_photo_analysis, user_id, limit=5):
        """
        Знаходить схожі фото з галереї юзера на основі аналізу фото клієнта

        Args:
            client_photo_analysis: результат аналізу фото клієнта
            user_id: ID юзера (власника салону)
            limit: кількість результатів

        Returns:
            list: схожі фото з описами
        """
        try:
            # Get all user's photos with analysis
            user_photos = Photo.objects.filter(
                user_id=user_id,
                is_processed=True
            ).exclude(detailed_analysis={})

            # Compare and score photos
            scored_photos = []

            for photo in user_photos:
                similarity_score = self._calculate_similarity(
                    client_photo_analysis,
                    photo.detailed_analysis
                )

                if similarity_score > 0.3:  # Threshold for similarity
                    scored_photos.append({
                        'photo_id': photo.id,
                        'file_path': photo.file_path,
                        'description': photo.description,
                        'analysis': photo.detailed_analysis,
                        'similarity_score': similarity_score
                    })

            # Sort by similarity score
            scored_photos.sort(key=lambda x: x['similarity_score'], reverse=True)

            return scored_photos[:limit]

        except Exception as e:
            print(f"Error finding similar photos: {e}")
            return []

    def _calculate_similarity(self, analysis1, analysis2):
        """
        Розраховує схожість між двома аналізами фото
        """
        score = 0.0

        # Same category gets high score
        if analysis1.get('category') == analysis2.get('category'):
            score += 0.4

        # Compare hair analysis if both present
        if (analysis1.get('hair_analysis', {}).get('present') and
            analysis2.get('hair_analysis', {}).get('present')):

            hair1 = analysis1['hair_analysis']
            hair2 = analysis2['hair_analysis']

            # Color similarity
            if hair1.get('color') == hair2.get('color'):
                score += 0.2

            # Length similarity
            if hair1.get('length') == hair2.get('length'):
                score += 0.15

            # Texture similarity
            if hair1.get('texture') == hair2.get('texture'):
                score += 0.1

            # Condition similarity
            if hair1.get('condition') == hair2.get('condition'):
                score += 0.15

        return min(score, 1.0)

    def generate_client_questions(self, client_photo_analysis, similar_photos):
        """
        Генерує питання для клієнта на основі аналізу його фото та схожих прикладів

        Args:
            client_photo_analysis: аналіз фото клієнта
            similar_photos: схожі фото з галереї

        Returns:
            dict: питання та рекомендації
        """
        try:
            # Prepare context
            similar_examples = []
            for photo in similar_photos[:3]:
                similar_examples.append({
                    'description': photo.get('description', ''),
                    'services': photo.get('analysis', {}).get('service_suggestions', [])
                })

            prompt = f"""
Based on the client's photo analysis and similar examples from our portfolio, generate helpful questions and recommendations.

Client's photo analysis:
{json.dumps(client_photo_analysis, indent=2)}

Similar examples from our portfolio:
{json.dumps(similar_examples, indent=2)}

Generate a response in JSON format:
{{
  "clarifying_questions": [
    "specific questions to ask the client to better understand their needs"
  ],
  "service_recommendations": [
    "recommended services based on analysis"
  ],
  "portfolio_matches": [
    "references to similar work from portfolio"
  ],
  "estimated_details": {{
    "duration": "estimated time",
    "complexity": "simple|moderate|complex",
    "special_requirements": ["any special requirements"]
  }},
  "client_message": "friendly message to send to the client in Ukrainian"
}}

Be specific and helpful. Ask questions that help clarify the client's desired outcome.
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a beauty salon assistant helping clients find the perfect service."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"Error generating questions: {e}")
            return {
                'clarifying_questions': [],
                'service_recommendations': [],
                'client_message': 'Дякую за фото! Ми проаналізуємо його і зв\'яжемося з вами найближчим часом.'
            }

    def _read_image(self, file_path):
        """Read image from local file or S3"""
        # For now, assume local file
        with open(file_path, 'rb') as image_file:
            return image_file.read()

    def _likelihood_name(self, likelihood):
        """Convert likelihood enum to string"""
        names = ['UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE', 'LIKELY', 'VERY_LIKELY']
        return names[likelihood] if 0 <= likelihood < len(names) else 'UNKNOWN'

    def _format_colors(self, colors):
        """Format color data for prompt"""
        return ', '.join([
            f"RGB({c['color']['red']}, {c['color']['green']}, {c['color']['blue']})"
            for c in colors
        ])
