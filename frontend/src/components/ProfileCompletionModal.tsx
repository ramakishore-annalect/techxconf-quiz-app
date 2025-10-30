import React, { useState } from 'react';
import { X } from 'lucide-react';
import Button from './ui/Button';
import Input from './ui/Input';
import { authApi } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import toast from 'react-hot-toast';

interface ProfileCompletionModalProps {
    isOpen: boolean;
    onClose: () => void;
    onComplete: () => void;
}

const ProfileCompletionModal: React.FC<ProfileCompletionModalProps> = ({
    isOpen,
    onClose,
    onComplete,
}) => {
    const { user, refreshUser } = useAuth();
    const [displayName, setDisplayName] = useState(user?.display_name || '');
    const [mobileNumber, setMobileNumber] = useState(user?.mobile_number || '');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [errors, setErrors] = useState<{ displayName?: string; mobileNumber?: string }>({});

    if (!isOpen) return null;

    const validateForm = (): boolean => {
        const newErrors: { displayName?: string; mobileNumber?: string } = {};

        if (!displayName.trim()) {
            newErrors.displayName = 'Name is required';
        }

        if (!mobileNumber.trim()) {
            newErrors.mobileNumber = 'Mobile number is required';
        } else {
            const cleaned = mobileNumber.replace(/[\s-]/g, '');
            if (!/^\d{10}$/.test(cleaned)) {
                newErrors.mobileNumber = 'Mobile number must be exactly 10 digits';
            }
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);
        try {
            await authApi.updateProfile({
                display_name: displayName.trim(),
                mobile_number: mobileNumber.replace(/[\s-]/g, ''),
            });

            // Refresh user data in context
            await refreshUser();

            toast.success('Profile completed successfully!');
            onComplete();
        } catch (error) {
            console.error('Failed to update profile:', error);
            toast.error('Failed to update profile. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" />

            {/* Modal */}
            <div className="flex min-h-full items-center justify-center p-4">
                <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-2xl font-bold text-gray-900">Complete Your Profile</h2>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-500 transition-colors"
                        >
                            <X className="h-6 w-6" />
                        </button>
                    </div>

                    {/* Description */}
                    <p className="text-gray-600 mb-6">
                        Please provide your name and mobile number to continue. This information will be
                        displayed on the leaderboard.
                    </p>

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label htmlFor="displayName" className="block text-sm font-medium text-gray-700 mb-1">
                                Full Name <span className="text-red-500">*</span>
                            </label>
                            <Input
                                id="displayName"
                                type="text"
                                value={displayName}
                                onChange={(e) => setDisplayName(e.target.value)}
                                placeholder="Enter your full name"
                                error={errors.displayName}
                                disabled={isSubmitting}
                            />
                            {errors.displayName && (
                                <p className="mt-1 text-sm text-red-600">{errors.displayName}</p>
                            )}
                        </div>

                        <div>
                            <label htmlFor="mobileNumber" className="block text-sm font-medium text-gray-700 mb-1">
                                Mobile Number (10 digits) <span className="text-red-500">*</span>
                            </label>
                            <Input
                                id="mobileNumber"
                                type="tel"
                                value={mobileNumber}
                                onChange={(e) => {
                                    // Allow only numbers and basic formatting characters
                                    const value = e.target.value.replace(/[^\d\s-]/g, '');
                                    setMobileNumber(value);
                                }}
                                placeholder="Enter 10-digit mobile number"
                                error={errors.mobileNumber}
                                maxLength={12}
                                disabled={isSubmitting}
                            />
                            {errors.mobileNumber && (
                                <p className="mt-1 text-sm text-red-600">{errors.mobileNumber}</p>
                            )}
                            <p className="mt-1 text-xs text-gray-500">
                                Example: 9876543210 or 98765-43210
                            </p>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-3 mt-6">
                            <Button
                                type="button"
                                variant="secondary"
                                onClick={onClose}
                                disabled={isSubmitting}
                                className="flex-1"
                            >
                                Cancel
                            </Button>
                            <Button
                                type="submit"
                                disabled={isSubmitting}
                                className="flex-1"
                            >
                                {isSubmitting ? 'Saving...' : 'Save & Continue'}
                            </Button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ProfileCompletionModal;
