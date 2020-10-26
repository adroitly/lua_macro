
--#if UNITY
--[[ AUTO_COMPLIME_START --
local a = "UNITY"
-- AUTO_COMPLIME_END ]] --
--#elseif ANDROID
local a = "ANDROID"
--#else
--[[ AUTO_COMPLIME_START --
local a = "WINDOWS"
-- AUTO_COMPLIME_END ]] --
--#endif

print(a)