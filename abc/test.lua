
--#if UNITY
local a = "UNITY"
--#elseif ANDROID
--[[ AUTO_COMPLIME_START --
local a = "ANDROID"
-- AUTO_COMPLIME_END ]] --
--#else
--[[ AUTO_COMPLIME_START --
local a = "WINDOWS"
-- AUTO_COMPLIME_END ]] --
--#endif

print(a)