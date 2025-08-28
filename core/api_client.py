import requests
import json
from typing import Iterator
import os
from dotenv import load_dotenv
import time
import traceback
import logging
from datetime import datetime
from pathlib import Path

load_dotenv()

def setup_logger():
    """Setup logger with both file and console handlers"""
    logs_dir = Path("api_logs/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger('api_client')
    logger.setLevel(logging.DEBUG)
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(funcName)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-5s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = logs_dir / f"api_client_{today}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    error_file = logs_dir / f"api_errors_{today}.log"
    error_handler = logging.FileHandler(error_file, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

class APIClient:
    """OpenRouter API client for RPA Code Assistant"""
    
    def __init__(self, config):
        logger.info("Initializing APIClient...")
        self.config = config
        self.base_url = config.OPENROUTER_BASE_URL
        self.model = config.MODEL_NAME
        self.headers = {
            "HTTP-Referer": "https://localhost",
            "X-Title": "RPA Code Assistant",  
            "Content-Type": "application/json"
        }
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Model: {self.model}")
        logger.info(f"API Key present: {'Yes' if self.api_key else 'No'}")
        
        if self.api_key:
            logger.debug(f"API Key length: {len(self.api_key)} characters")
            logger.debug(f"API Key preview: {self.api_key[:10]}...")
        else:
            logger.error("No API key found in environment variables!")
            
        logger.info(f"Max tokens: {config.MAX_TOKENS}")
        logger.info(f"Temperature: {config.TEMPERATURE}")
        logger.info("APIClient initialization completed")
    
    def _update_headers(self):
        """Update headers with API key from environment"""
        logger.debug("Updating headers...")
        
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
            logger.debug("Authorization header added successfully")
        else:
            logger.error("No API key available to add to headers")
            return False
        
        safe_headers = {
            k: v[:20] + '...' if k == 'Authorization' and len(v) > 20 else v 
            for k, v in self.headers.items()
        }
        logger.debug(f"Final headers: {json.dumps(safe_headers, indent=2)}")
        return True
    
    def validate_api_key(self) -> bool:
        """Validate if the API key is working"""
        logger.info("Starting API key validation...")
        
        try:
            if not self._update_headers():
                logger.error("Failed to update headers - no API key")
                return False
            
            if "Authorization" not in self.headers:
                logger.error("No Authorization header found after update")
                return False
            
            test_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            }
            
            logger.info("Sending validation request...")
            logger.debug(f"Request URL: {self.base_url}/chat/completions")
            logger.debug(f"Request data: {json.dumps(test_data, indent=2)}")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=test_data,
                timeout=10
            )
            end_time = time.time()
            
            duration = end_time - start_time
            logger.info(f"Request completed in {duration:.2f} seconds")
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                logger.error(f"API validation failed with status {response.status_code}")
                logger.error(f"Response text: {response.text}")
                
                try:
                    error_json = response.json()
                    logger.error(f"Error details: {json.dumps(error_json, indent=2)}")
                except Exception as parse_error:
                    logger.error(f"Could not parse error response as JSON: {parse_error}")
                
                return False
            else:
                logger.info("API key validation successful!")
                
                try:
                    response_json = response.json()
                    logger.debug(f"Validation response: {json.dumps(response_json, indent=2)}")
                except Exception as parse_error:
                    logger.warning(f"Could not parse success response as JSON: {parse_error}")
            
            return True
            
        except requests.exceptions.Timeout:
            logger.error("API validation timed out after 10 seconds")
            return False
        except requests.exceptions.ConnectionError as ce:
            logger.error(f"Connection error during validation: {str(ce)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during API validation: {str(e)}")
            logger.error(f"Validation traceback: {traceback.format_exc()}")
            return False
    
    def create_chat_completion(self, messages: list, stream: bool = False) -> Iterator[str]:
        """Create a chat completion with streaming support"""
        logger.info("Starting chat completion...")
        logger.info(f"Stream mode: {stream}")
        logger.info(f"Number of messages: {len(messages)}")
        
        preview_messages = messages[-2:] if len(messages) > 2 else messages
        logger.debug(f"Messages preview: {json.dumps(preview_messages, indent=2)}")
        
        try:
            if not self._update_headers():
                raise Exception("Failed to update headers - no API key available")
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.config.MAX_TOKENS,
                "temperature": self.config.TEMPERATURE,
                "stream": stream
            }
            
            logger.info("Request parameters:")
            logger.info(f"Model: {data['model']}")
            logger.info(f" Max tokens: {data['max_tokens']}")
            logger.info(f"Temperature: {data['temperature']}")
            logger.info(f"Stream: {data['stream']}")
            
            logger.info("Sending chat completion request...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                stream=stream,
                timeout=60
            )
            
            initial_duration = time.time() - start_time
            logger.info(f"Initial response received in {initial_duration:.2f} seconds")
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            logger.debug("Response status check passed")
            
            if stream:
                logger.info("Processing streaming response...")
                yield from self._process_streaming_response(response, start_time)
            else:
                logger.info("Processing non-streaming response...")
                yield from self._process_regular_response(response, start_time)
                
        except requests.exceptions.Timeout:
            error_msg = "Request timed out after 60 seconds"
            logger.error(error_msg)
            raise Exception("API request failed: Request timed out")
            
        except requests.exceptions.ConnectionError as ce:
            error_msg = f"Connection error: {str(ce)}"
            logger.error(error_msg)
            raise Exception(f"API request failed: Connection error - {str(ce)}")
            
        except requests.exceptions.HTTPError as he:
            error_msg = f"HTTP error: {str(he)}"
            logger.error(error_msg)
            if he.response:
                logger.error(f"HTTP error response: {he.response.text}")
                raise Exception(f"API request failed: HTTP {he.response.status_code} - {he.response.text}")
            else:
                raise Exception(f"API request failed: {str(he)}")
                
        except requests.exceptions.RequestException as re:
            error_msg = f"Request exception: {str(re)}"
            logger.error(error_msg)
            logger.error(f"Request exception traceback: {traceback.format_exc()}")
            raise Exception(f"API request failed: {str(re)}")
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Unexpected error traceback: {traceback.format_exc()}")
            raise Exception(f"Unexpected error: {str(e)}")
    
    def _process_streaming_response(self, response, start_time) -> Iterator[str]:
        """Process streaming response with detailed logging"""
        chunk_count = 0
        total_content = ""
        
        logger.debug("Starting to process streaming chunks...")
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                logger.debug(f"Raw line: {repr(line[:100])}...")
                
                if line.startswith('data: '):
                    line = line[6:] 
                    logger.debug(f"After prefix removal: {repr(line[:100])}...")
                    
                    if line.strip() == '[DONE]':
                        total_time = time.time() - start_time
                        logger.info(f"Stream completed with [DONE] marker")
                        logger.info(f"Final stats: {chunk_count} chunks, {len(total_content)} characters, {total_time:.2f}s total")
                        break
                        
                    try:
                        chunk_data = json.loads(line)
                        logger.debug(f"Parsed chunk: {json.dumps(chunk_data, indent=2)}")
                        
                        if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                            delta = chunk_data['choices'][0].get('delta', {})
                            
                            if 'content' in delta and delta['content']:
                                content = delta['content']
                                chunk_count += 1
                                total_content += content
                                
                                logger.debug(f"✨ Chunk #{chunk_count}: {repr(content)}")
                                if chunk_count % 10 == 0:
                                    logger.info(f"Progress: {chunk_count} chunks, {len(total_content)} chars")
                                
                                yield content
                                
                            else:
                                logger.debug("No content in delta or content is empty")
                        else:
                            logger.debug("No choices in chunk data")
                            
                    except json.JSONDecodeError as je:
                        logger.warning(f"JSON decode error: {str(je)}")
                        logger.warning(f"Problematic line: {repr(line[:200])}")
                        continue
                        
                    except Exception as ce:
                        logger.error(f"Chunk processing error: {str(ce)}")
                        logger.debug(f"Chunk error traceback: {traceback.format_exc()}")
                        continue
                else:
                    logger.debug("⏭️ Line doesn't start with 'data: ', skipping")
        
        final_time = time.time() - start_time
        logger.info(f"Streaming completed successfully!")
        logger.info(f"Total chunks: {chunk_count}")
        logger.info(f"Total content length: {len(total_content)} characters")
        logger.info(f"Total processing time: {final_time:.2f} seconds")
        
        if chunk_count == 0:
            logger.error("WARNING: No content chunks were yielded!")
    
    def _process_regular_response(self, response, start_time) -> Iterator[str]:
        """Process regular (non-streaming) response with detailed logging"""
        try:
            response_data = response.json()
            logger.debug(f"Full response: {json.dumps(response_data, indent=2)}")
            
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0]['message']['content']
                content_length = len(content) if content else 0
                
                logger.info(f"Extracted content length: {content_length} characters")
                logger.debug(f"Content preview: {repr(content[:200]) if content else 'None'}...")
                
                if content:
                    total_time = time.time() - start_time
                    logger.info(f"Non-streaming response processed successfully in {total_time:.2f}s")
                    yield content
                else:
                    logger.error("Content is empty!")
            else:
                logger.error("No choices in response data")
                logger.error(f"Response structure keys: {list(response_data.keys())}")
                
        except json.JSONDecodeError as je:
            logger.error(f"Failed to parse response JSON: {str(je)}")
            logger.error(f"Raw response: {response.text[:500]}...")
            raise Exception(f"Failed to parse API response: {str(je)}")

def get_api_client():
    """Get configured API client instance"""
    logger.info("Creating API client instance...")
    
    try:
        from core.config import load_config
        config = load_config()
        logger.debug("Config loaded successfully")
        
        client = APIClient(config)
        logger.info("API client created successfully")
        return client
        
    except Exception as e:
        logger.error(f"ERROR creating API client: {str(e)}")
        logger.error(f"API client creation traceback: {traceback.format_exc()}")
        return None