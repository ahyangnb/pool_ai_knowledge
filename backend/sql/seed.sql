-- ============================================================
-- Pool AI Knowledge - Seed Data (default admin & config)
-- Only inserts when data does not already exist.
-- ============================================================

-- Default super admin: admin / admin123456
INSERT INTO `admin_users` (`username`, `email`, `password_hash`, `is_active`, `is_super_admin`)
SELECT 'admin', 'admin@example.com',
       '$2b$12$NsHUq2/S42CBqax/GHGUQOFSq3V6a9/KYbsItoKkcUFFDlhttAv2W',
       1, 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM `admin_users` WHERE `username` = 'admin');
