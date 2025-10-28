import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Send, Image as ImageIcon, X } from "lucide-react";

interface InputFormProps {
  onSubmit: (query: string, images?: File[]) => void;
  isLoading: boolean;
  context?: 'homepage' | 'chat'; // Add new context prop
}

export function InputForm({ onSubmit, isLoading, context = 'homepage' }: InputFormProps) {
  const [inputValue, setInputValue] = useState("");
  const [uploadedImages, setUploadedImages] = useState<File[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if ((inputValue.trim() || uploadedImages.length > 0) && !isLoading) {
      onSubmit(inputValue.trim() || "Analyze these images", uploadedImages.length > 0 ? uploadedImages : undefined);
      setInputValue("");
      setUploadedImages([]);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    setUploadedImages(prev => [...prev, ...imageFiles].slice(0, 5)); // Max 5 images
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeImage = (index: number) => {
    setUploadedImages(prev => prev.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const placeholderText =
    context === 'chat'
      ? "What's your next startup concept?"
      : "What's your GTM idea?";

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col justify-center items-center h-full gap-2"
    >
      <div className="flex items-stretch gap-2 w-full">
        <Textarea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholderText}
          rows={1}
          className="flex-1 resize-none min-h-0 h-10 px-3 py-2 text-center"
        />
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          onChange={handleImageUpload}
          className="hidden"
        />
        <Button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          variant="outline"
          className="h-10 px-3 flex items-center justify-center"
        >
          <ImageIcon className="h-4 w-4" />
        </Button>
        <Button
          type="submit"
          disabled={isLoading || (!inputValue.trim() && uploadedImages.length === 0)}
          className="h-10 px-4 flex items-center justify-center"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </Button>
      </div>
      {uploadedImages.length > 0 && (
        <div className="w-full grid grid-cols-5 gap-2 mt-2">
          {uploadedImages.map((file, idx) => {
            const url = URL.createObjectURL(file);
            return (
              <div key={`${file.name}-${idx}`} className="relative group">
                <img
                  src={url}
                  alt={file.name}
                  className="w-full h-16 object-cover rounded border"
                  onLoad={() => URL.revokeObjectURL(url)}
                />
                <button
                  type="button"
                  onClick={() => removeImage(idx)}
                  className="absolute -top-2 -right-2 bg-black/60 text-white rounded-full p-1 opacity-80 hover:opacity-100"
                  aria-label="Remove image"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </form>
  );
}
