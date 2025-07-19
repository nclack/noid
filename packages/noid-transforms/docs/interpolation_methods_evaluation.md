# Interpolation and Extrapolation Methods

## Brief

This report describes the interpolation and extrapolation methods proposed for
the transforms schema, focusing on:

1. Parameter requirements (only parameter-free methods are included)
2. Library support (scipy, OpenCV, ITK)
3. Dimensional restrictions
4. Standardization across libraries

## Interpolation methods

### ✅ RECOMMENDED (Parameter-free, well-supported)

**linear**
- **Definition**: Linear interpolation in N dimensions
- **Dimensionality**: 1D to nD supported
- **Libraries**: scipy (interp1d, interpn), OpenCV (INTER_LINEAR for 2D), ITK
  (LinearInterpolateImageFunction)
- **Parameters**: None required
- **Notes**: Default in many libraries, good speed/quality balance

**nearest**
- **Definition**: Nearest neighbor interpolation
- **Dimensionality**: 1D to nD supported
- **Libraries**: scipy (interp1d 'nearest'), OpenCV (INTER_NEAREST), ITK
  (NearestNeighborInterpolateImageFunction)
- **Parameters**: None required
- **Notes**: Fastest method, preserves original values exactly

**cubic**
- **Definition**: Cubic spline interpolation (1D) or bicubic (2D)
- **Dimensionality**: 1D, 2D well-supported; nD varies by library
- **Libraries**: scipy (interp1d 'cubic', CubicSpline), OpenCV (INTER_CUBIC for
  2D), ITK (3rd order BSpline default)
- **Parameters**: None required (uses default cubic order)
- **Notes**: Higher quality than linear, moderate computational cost


### ⚠️ CONDITIONAL (2D-specific or limited dimensionality)

**bilinear**
- **Definition**: Linear interpolation in 2D using 2x2 neighborhood
- **Dimensionality**: 2D only
- **Libraries**: OpenCV (INTER_LINEAR), PIL, various image libraries
- **Parameters**: None required
- **Notes**: Technically a subset of 'linear' for 2D cases

**bspline**:
- **Issue**: Requires spline order parameter (0-5 in ITK)
- **Libraries**: ITK (BSplineInterpolateImageFunction), scipy
  (make_interp_spline)
- **Recommendation**: Use 'cubic' instead (equivalent to 3rd order B-spline)

### ❌ REJECTED (Require parameters or poorly standardized)

**area**
- **Definition**: Pixel area resampling (optimal for downsampling)
- **Dimensionality**: 2D primary, some nD support
- **Libraries**: OpenCV (INTER_AREA)
- **Parameters**: None required
- **Notes**: Preferred for image downsampling, reduces aliasing. Rejected
  because it's not clear what the algorithm is, or what it's equivalent
  would be in other libraries.

**lanczos**
- **Issue**: Requires window size parameter (commonly 2, 3, or 4)
- **Libraries**: OpenCV (INTER_LANCZOS4), PIL, ImageMagick
- **Recommendation**: Remove - cannot be parameter-free

**bicubic**
- **Definition**: Cubic interpolation in 2D using 4x4 neighborhood
- **Dimensionality**: 2D only
- **Libraries**: OpenCV (INTER_CUBIC), PIL, various image libraries
- **Parameters**: None required
- **Notes**: Technically a subset of 'cubic' for 2D cases

**spline**
- **Issue**: Too generic, requires order specification
- **Libraries**: scipy (various spline functions)
- **Recommendation**: Use 'cubic' for 3rd order, 'linear' for 1st order

**sinc**
- **Issue**: Requires windowing function and parameters
- **Libraries**: DSP libraries, custom implementations
- **Recommendation**: Remove - theoretical ideal but requires windowing

**quadratic**
- **Issue**: Limited library support, often requires parameters
- **Libraries**: scipy (interp1d 'quadratic'), some custom implementations
- **Recommendation**: Remove - 'cubic' is more standard

## Extrapolation methods

### ✅ RECOMMENDED (Parameter-free, well-supported)

**nearest**
- **Definition**: Extend using nearest boundary value
- **Dimensionality**: 1D to nD supported
- **Libraries**: scipy.ndimage (mode='nearest'), numpy (mode='edge')
- **Parameters**: None required
- **Notes**: Equivalent to 'edge' in some libraries

**constant** (alias: **zero**)
- **Definition**: Extend using constant value (typically 0)
- **Dimensionality**: 1D to nD supported
- **Libraries**: scipy.ndimage (mode='constant'), numpy (mode='constant')
- **Parameters**: None required (uses 0 as default)
- **Notes**: 'zero' is clearer than 'constant' for default behavior

**reflect**
- **Definition**: Reflect about boundary edge (half-sample symmetric)
- **Dimensionality**: 1D to nD supported
- **Libraries**: scipy.ndimage (mode='reflect'), numpy (mode='reflect')
- **Parameters**: None required
- **Notes**: Well-defined mathematical operation

**wrap**
- **Definition**: Wrap around to opposite boundary (periodic)
- **Dimensionality**: 1D to nD supported
- **Libraries**: scipy.ndimage (mode='wrap'), numpy (mode='wrap')
- **Parameters**: None required
- **Notes**: Assumes periodic boundary conditions


### ⚠️ CONDITIONAL (Library-specific naming)

**edge**
- **Definition**: Replicate boundary values (same as 'nearest')
- **Libraries**: numpy (mode='edge'), some image libraries
- **Recommendation**: Use 'nearest' for consistency

### ❌ REJECTED (Require parameters or poorly defined)

**linear**
- **Issue**: Requires slope parameter for extrapolation
- **Libraries**: Various custom implementations
- **Recommendation**: Remove - needs parameters

**smooth**
- **Issue**: Vague definition, requires smoothing parameters
- **Libraries**: Various custom implementations
- **Recommendation**: Remove - not well-defined

**polynomial**
- **Issue**: Requires polynomial degree and coefficients
- **Libraries**: scipy (extrapolate with polynomial fits)
- **Recommendation**: Remove - needs parameters

**mirror**
- **Definition**: Reflect about center of boundary pixel (whole-sample symmetric)
- **Dimensionality**: 1D to nD supported
- **Libraries**: scipy.ndimage (mode='mirror')
- **Parameters**: None required
- **Notes**: Different from 'reflect' in sample positioning, but too similar.
  Not clear which to choose based on name.

## FINAL RECOMMENDATIONS

### Interpolation Methods (parameter-free, well-supported)
1. **linear** - General N-dimensional linear interpolation
2. **nearest** - Nearest neighbor interpolation
3. **cubic** - Cubic spline (1D) or bicubic (2D) interpolation
4. **area** - Area-based resampling (optimal for downsampling)

### Extrapolation Methods (parameter-free, well-supported)
1. **nearest** - Extend using nearest boundary value
2. **zero** - Extend using zero (constant) values
3. **reflect** - Reflect about boundary edge
4. **wrap** - Wrap around periodically
5. **mirror** - Reflect about boundary center

### Optional 2D-Specific Methods
If supporting 2D-specific terminology:
- **bilinear** (equivalent to 'linear' in 2D)
- **bicubic** (equivalent to 'cubic' in 2D)

## Implementation Notes

1. **Library Consistency**: The recommended methods are supported across scipy,
OpenCV, and ITK with consistent behavior
2. **Parameter Requirements**: All recommended methods work without additional
parameters
3. **Dimensional Support**: Focus on methods that work in arbitrary dimensions,
with notes for 2D-specific cases
4. **Naming Conventions**: Use the most widely adopted names across libraries
5. **Default Behaviors**: Methods use sensible defaults (e.g., 'zero' uses 0 as
constant value)

This validation ensures that the transform schema includes only robust,
parameter-free interpolation and extrapolation methods that are well-supported
across major scientific computing libraries.
