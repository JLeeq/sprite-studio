-- =====================================================
-- Supabase Database Schema for 2D Game Asset Generator
-- =====================================================
-- 이 SQL 파일을 Supabase Dashboard > SQL Editor에서 실행하세요
-- 또는 Supabase CLI를 사용하여 마이그레이션으로 적용하세요

-- =====================================================
-- 1. user_tokens 테이블 (토큰 관리)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.user_tokens (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    tokens INTEGER NOT NULL DEFAULT 10,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- RLS (Row Level Security) 정책 설정
ALTER TABLE public.user_tokens ENABLE ROW LEVEL SECURITY;

-- 사용자는 자신의 토큰만 조회 가능
CREATE POLICY "Users can view their own tokens"
    ON public.user_tokens
    FOR SELECT
    USING (auth.uid() = user_id);

-- =====================================================
-- 2. user_projects 테이블 (프로젝트 관리)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.user_projects (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_name TEXT NOT NULL DEFAULT 'Default Project',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 추가 (조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_user_projects_user_id 
    ON public.user_projects(user_id);
CREATE INDEX IF NOT EXISTS idx_user_projects_user_name 
    ON public.user_projects(user_id, project_name);

-- RLS 정책 설정
ALTER TABLE public.user_projects ENABLE ROW LEVEL SECURITY;

-- 사용자는 자신의 프로젝트만 조회/생성 가능
CREATE POLICY "Users can view their own projects"
    ON public.user_projects
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own projects"
    ON public.user_projects
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- =====================================================
-- 3. generated_images 테이블 (생성된 이미지 메타데이터)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.generated_images (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES public.user_projects(id) ON DELETE CASCADE,
    image_type TEXT NOT NULL,
    image_url TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_generated_images_user_id 
    ON public.generated_images(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_images_project_id 
    ON public.generated_images(project_id);
CREATE INDEX IF NOT EXISTS idx_generated_images_created_at 
    ON public.generated_images(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_generated_images_user_created 
    ON public.generated_images(user_id, created_at DESC);

-- RLS 정책 설정
ALTER TABLE public.generated_images ENABLE ROW LEVEL SECURITY;

-- 사용자는 자신의 이미지만 조회 가능
CREATE POLICY "Users can view their own generated images"
    ON public.generated_images
    FOR SELECT
    USING (auth.uid() = user_id);

-- =====================================================
-- 4. updated_at 자동 업데이트 함수
-- =====================================================
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- updated_at 트리거 추가
CREATE TRIGGER update_user_tokens_updated_at
    BEFORE UPDATE ON public.user_tokens
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER update_user_projects_updated_at
    BEFORE UPDATE ON public.user_projects
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- =====================================================
-- 5. 스토리지 버킷 생성 (Storage > Buckets에서 수동 생성 권장)
-- =====================================================
-- 참고: Supabase Dashboard > Storage > Create Bucket에서 수동으로 생성하세요
-- 버킷 이름: "generated"
-- Public bucket: Yes (공개 URL 접근 필요)
-- File size limit: 원하는 최대 크기 (예: 10MB)
-- Allowed MIME types: image/png, image/jpeg, image/jpg, image/gif, image/webp

-- 또는 SQL로 생성하려면:
-- INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
-- VALUES (
--     'generated',
--     'generated',
--     true,
--     10485760, -- 10MB
--     ARRAY['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
-- );

-- =====================================================
-- 6. 스토리지 정책 설정 (Storage RLS)
-- =====================================================
-- Storage > Policies에서 수동으로 설정하거나 아래 SQL 사용:

-- 모든 사용자가 업로드 가능 (서비스 역할 키로 백엔드에서 업로드)
-- INSERT 정책: 서비스 역할 키만 업로드 가능하므로 RLS 정책은 필요 없음
-- SELECT 정책: 공개 버킷이므로 모든 사람이 읽기 가능

-- =====================================================
-- 완료!
-- =====================================================
-- 다음 단계:
-- 1. Supabase Dashboard > Storage > Create Bucket에서 "generated" 버킷 생성 (Public)
-- 2. 환경 변수 설정 (.env 파일)
--    - SUPABASE_URL
--    - SUPABASE_ANON_KEY
--    - SUPABASE_SERVICE_ROLE_KEY
-- 3. 테스트 실행


