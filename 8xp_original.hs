import qualified Data.ByteString as B
import qualified Data.List as L
import qualified Data.Char as C
import Data.Word
import Data.Bits
import System

--The TI character set is really weird.
charmap = zip "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-, \n:()^/*+?![]{}<>='\"" 
	$ [[0xbb,0xb0],[0xbb,0xb1],[0xbb,0xb2],[0xbb,0xb3],[0xbb,0xb4],[0xbb,0xb5],[0xbb,0xb6],[0xbb,0xb7],
	[0xbb,0xb8],[0xbb,0xb9],[0xbb,0xba],[0xbb,0xbc],[0xbb,0xbd],[0xbb,0xbe],[0xbb,0xbf],[0xbb,0xc0],
	[0xbb,0xc1],[0xbb,0xc2],[0xbb,0xc3],[0xbb,0xc4],[0xbb,0xc5],[0xbb,0xc6],[0xbb,0xc7],[0xbb,0xc8],
	[0xbb,0xc9],[0xbb,0xca]] ++ map (:[]) [0x41,0x42,0x43,0x44,0x45,0x46,0x47,0x48,0x49,0x4a,0x4b,0x4c,
	0x4d,0x4e,0x4f,0x50,0x51,0x52,0x53,0x54,0x55,0x56,0x57,0x58,0x59,0x5a,0x30,0x31,0x32,0x33,0x34,0x35,
	0x36,0x37,0x38,0x39,0x3a,0x71,0x2b,0x29,0x3f,0x3e,0x10,0x11,0xf0,0x83,0x82,0x70,0xaf,0x2d,0x06,0x07,
	0x08,0x09,0x6b,0x6c,0x6a,0xae,0x2a]

--Transform a string into TI format.
mapToCalc :: [Char] -> [Int]
mapToCalc s = concat . map lookup $ s where
	lookup c = let a = L.lookup c charmap in case a of
		Just n -> n; Nothing -> [58] --If character is not recognized, replace with period.

--Little endian: Numbers stored in reverse bit order.
reverseEncode :: Int -> [Int]
reverseEncode k = [k .&. 0xFF, k `shiftR` 8]

padZeroes :: [Int] -> [Int]
padZeroes xs = xs ++ replicate (8-length xs) 0

{- Explanation of the 8xp file format

The first 11 bytes must contain "**TI83F", 1a, 0a, 0.
Then the next 42 bytes can contain whatever you want. Here I filled it with 0's.
Next, 2 bytes for length of program + 19.

From now on, the file is checksummed. This is the sum of all the bytes.
Start with 0d and 0.
Then the length (again) + 2.
Then, either 05 for unprotected (editable), or 06 for protected (not editable).
Then the program name. Must be exactly 8 characters, all [A-Z0-9]. The first character
cannot be a number. If it's less than 8 characters, pad the rest with 0's.
Then, 0 and 0. This is the version number.
Put the length (again) + 2.
Put the length (again). No +2 this time.
Now dump the contents of the file. This should be in the TI encoding, not ASCII, of course.
Finally, write the checksum. We're done.  -}

--n: prog name, must already be all uppercase, <= 8 length.
--s: contents
encodeAll :: String -> String -> [Word8]
encodeAll n s = map fromIntegral $ concat [map C.ord "**TI83F*",[0x1a,0x0a],replicate 43 0,
		reverseEncode (len+19),cs,reverseEncode (sum cs)] where
	s' = mapToCalc s
	len = length s'
	--cs is the checksummed portion.
	cs = concat [[0x0d,0x00],reverseEncode (len+2),[0x05],padZeroes (map C.ord n),
		[0x00,0x00],reverseEncode (len+2),reverseEncode len,s']

--Make a file name suitable to be a program name
adjustName :: String -> String
adjustName s = map C.toUpper . take 8 . filter C.isAlphaNum .
	dropWhile (not . C.isAlpha) . takeWhile (/='.') . flip drop s .
	(\x -> if null x then 0 else last x) . L.findIndices (`elem` "\\/") $ s
	
main = do
	args <- getArgs
	mapM_ process args where
		process f = do
			file <- readFile f
			let pname = adjustName f
			B.writeFile (pname ++ ".8xp") . B.pack $ encodeAll pname file

