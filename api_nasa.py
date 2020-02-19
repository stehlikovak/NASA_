import requests
import json
from pprint import pprint 
from collections import namedtuple

class NasaObject:
    """general class to get response and collection of files from NASA API"""

    def __init__(self, keywords, title, media_type, year_start, year_end):
        self.keywords = keywords
        self.title = title
        self.media_type = media_type
        self.year_start = year_start
        self.year_end = year_end

    def get_response(self):
        url = "https://images-api.nasa.gov/search"
        response = requests.get(url, params=self.parameters)
        # print(response)
        return response

    def print_response(self, response):
        # print(response)
        if response:
            print(f'Request is successful: {response}.')
        else:
            print(f'Request returned an error: {response}.')

    def get_json_links(self, response):
        json_links = []
        for response_link in response.json()['collection']['items']:
            json_links.append(response_link['href'])
        # print(len(self.json_links)) 
        # pprint(self.json_links)
        return json_links

class Image(NasaObject):
    """subclass for selecting a collection of images, an image collection contain links to images with different resolution, links containing "orig" in name were selected, usually orig.tif or orig.jpg""" 

    def __init__(self, description, keywords, title, media_type, year_start, year_end):
        super().__init__(keywords, title, media_type, year_start, year_end)
        self.description = description
        self.parameters = {"description" : self.description, 
                            "keywords" : self.keywords,
                            "title" : self.title,         
                            "media_type" : self.media_type,
                            "year_start" : self.year_start,
                            "year_end" : self.year_end,                
                             } 

    def get_collection(self, json_links, count):
        # pprint(json_links)
        open_links = []
        for json_link in json_links:
            link_response = requests.get(json_link).json() 
            open_links.append(link_response)
        # pprint(open_links)
        orig_images = []
        for item in open_links:
            # print(item)
            for link in item:
                if "orig" in link:
                    orig_images.append(link)
        # print(len(orig_images))
        # print(type(orig_images)) 
        print(f"{count} images of Mars surface are: \n{chr(10).join(orig_images[:count])}")    
        return orig_images



class Video(NasaObject):
    """subclass for selecting a collection of videos, with method for checking if results give only video files """
    def __init__(self, keywords, title, media_type, year_start, year_end):
            super().__init__(keywords, title, media_type, year_start, year_end)
            self.parameters = { "keywords" : self.keywords,
                                "title" : self.title,         
                                "media_type" : self.media_type,
                                "year_start" : self.year_start,
                                "year_end": self.year_end,                
                                } 

    def classify_links(self, json_links):
        yes_video_links = []
        non_video_links = []
        # print(type(self.json_links))
        for json_link in json_links:
            link_response = requests.get(json_link).json() 
            # print(type(link_response))
            # pprint(link_response)
            try:
                for link in link_response:
                    # print(link)
                    if "mp4" in link:
                        if json_link not in yes_video_links:
                            yes_video_links.append(json_link) 
                    else:
                        if json_link not in non_video_links:
                            non_video_links.append(json_link) 
            except:
                pass

        return yes_video_links, non_video_links


    def compare_links(self, yes_video_links, non_video_links):
        yes_video_links = yes_video_links.sort()
        non_video_links = non_video_links.sort()
        
        if yes_video_links == non_video_links:
            return True
            
        else:
            return False
                   

    def get_mp4_files(self, json_links):
        for json_link in json_links:
            # print(json_link)
            link_response = (requests.get(json_link)).json()
            mp4_files = []
            for link in link_response:
                if "mp4" in link:
                    mp4_files.append(link)
            return mp4_files
            

    def contain_atNASA(self, json_links):
        json_notfunc = []
        for item in json_links:
            if '@NASA' in item:
                json_notfunc.append(item)
        return json_notfunc      

def main():
    image = Image(description = "planet Mars surface, image", 
                    keywords = "Mars, Mars surface",
                    title = "Mars",         
                    media_type = "image",
                    year_start = "2018",
                    year_end = "2018")
    response = image.get_response()
    image.print_response(response)
    json_links = image.get_json_links(response)
    image.get_collection(json_links, 5)



    video = Video( "Mars",
                    "Mars",         
                    "video",
                    "2018",
                    "2018")
    response = video.get_response()
    video.print_response(response)
    json_links = video.get_json_links(response)

    yes_video_links, non_video_links = video.classify_links(json_links)

    if video.compare_links(yes_video_links, non_video_links) == True:
        print("RESULT OF COMPARISON: NASA records with keyword Mars taken in 2018 with media_type='video' refer to video and non-video type of files.")
        print(f"These records contain links to video: \n{chr(10).join(yes_video_links)}")
        # print(f"These records contain links to other type of media files: \n{chr(10).join(non_video_links)}")
    else:
        print("RESULT OF COMPARISON: Some links contain only one (video or non-video) type of files.")

    mp4_files = video.get_mp4_files(json_links)
    for i in json_links:
        pprint(f"WEB LINK n.:{(json_links.index(i)+1)} - {i} - LINKS TO VIDEO: {mp4_files}")


    json_notfunc = video.contain_atNASA(json_links)
    print(f"This links may not contain functional link to video (return error: Access denied): \n{chr(10).join(json_notfunc)}")
   

if __name__ == "__main__":
    main()

