//! Paradox Mod Translator - AI-powered translation tool for Paradox game mods.

pub mod config;
pub mod postprocess;
pub mod preprocess;
pub mod translate;
pub mod utils;

pub mod error;

// Re-export commonly used types
pub use error::{Result, TranslationError};

#[cfg(test)]
mod tests {
    // Keep existing test structure for now
    #[test]
    fn it_works() {
        // Simple placeholder test
        assert_eq!(2 + 2, 4);
    }
}
